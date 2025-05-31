from flask import Flask, render_template, url_for, jsonify, redirect, request
import  os, csv, re, asyncio, aiohttp, math
from backend.arbolB import BTree, CalificacionNodo
from backend.carga_csv import cargar_lugares_csv, guardar_lugar_en_csv, guardar_calificacion_csv,cargar_calificaciones_csv, guardar_recomendaciones_csv, insertar_calificacion_en_arbol 
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
from backend.modelos.GrafoPonderado import generar_grafo_ponderado  
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Recarga automática de plantillas
API_KEY = os.getenv("AIzaSyBPe0eVEKRRzjfZod6BLf7TQxRNxz51xTc")
cache_tiempos_traslado = {}


#Diccionario para crear arboles segun el tipo de actividad
arbol_lugares = BTree(grado=5) # Para turismo, comida, entretenimiento
arbol_hospedaje = BTree(grado=5)  # Para hospedaje
arbol_calificaciones = BTree(grado=5) #Para las calificaciones

# Carga automática del CSV al iniciar el servidor
try:
    with open('data/datos.csv', 'r', encoding='utf-8-sig') as archivo_csv:
        cargar_lugares_csv(archivo_csv, arbol_lugares, arbol_hospedaje)
    print("Lugares y hospedajes cargados correctamente")

    cargar_calificaciones_csv("data/ratings.csv", arbol_calificaciones, arbol_lugares)
    print("Calificaciones cargadas correctamente")

    # Exportar árboles
    UtilidadesGrafo.exportarArbol(arbol_lugares, "arbol_lugares")
    UtilidadesGrafo.exportarArbol(arbol_hospedaje, "arbol_hospedajes")
    UtilidadesGrafo.exportarArbol(arbol_calificaciones, "arbol_calificaciones")

    print(f"Lugares cargados: {len(arbol_lugares.obtener_lugares())}")
    print(f"Hospedajes cargados: {len(arbol_hospedaje.obtener_lugares())}")
    print(f"Calificaciones cargadas: {len(arbol_calificaciones.obtener_calificaciones())}")

except Exception as e:
    print(f"Error al cargar datos: {e}")



#FUNCION PARA SEGUIR LOS ID'S DEL ARCHIVO DATOS.CSV
def obtener_siguiente_id(path='data/datos.csv'):
    id_max = 0
    if os.path.exists(path):
        with open(path, newline='') as archivo:
            reader = csv.reader(archivo)
            for fila in reader:
                try:
                    id_actual = int(fila[0])
                    id_max = max(id_max, id_actual)
                except:
                    continue
    return id_max + 1



#API PARA CALIFICACIONES
ARCHIVO = "./data/datos.csv"


def obtener_lugar_por_id(id_lugar):
    # Leer todos los lugares, devolver objeto lugar que tenga id_lugar
    with open(ARCHIVO, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # saltar header
        for fila in reader:
            if int(fila[0]) == id_lugar:
                # Crear un objeto simple para representar lugar (o usar tu clase Lugar)
                lugar = type('Lugar', (), {})()
                lugar.id = int(fila[0])
                lugar.departamento = fila[1]
                lugar.municipio = fila[2]
                lugar.nombre = fila[3]
                lugar.tipo = fila[4]
                lugar.direccion = fila[5]
                lugar.latitud = float(fila[6])
                lugar.longitud = float(fila[7])
                lugar.calificacion = float(fila[8]) if fila[8] else 0.0
                lugar.precio = float(fila[9]) if fila[9] else 0.0
                lugar.tiempo_estadia = float(fila[10]) if fila[10] else 0.0
                lugar.cantidad_calificaciones = getattr(lugar, 'cantidad_calificaciones', 0)

                return lugar
    return None


def guardar_lugar(lugar):
    # Leer todo el CSV, actualizar el lugar con id_lugar, reescribir el CSV
    lugares = []
    with open(ARCHIVO, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for fila in reader:
            if int(fila[0]) == lugar.id:
                # Actualizar la calificación promedio en la columna índice 8
                fila[8] = f"{lugar.calificacion:.2f}"
            lugares.append(fila)

    with open(ARCHIVO, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(lugares)


def calcular_promedio_calificaciones(arbol_calificaciones, id_lugar):
    calificaciones = arbol_calificaciones.obtener_todas_calificaciones_por_id(id_lugar)
    if not calificaciones:
        return 0.0
    suma = sum(c.puntaje for c in calificaciones)
    promedio = suma / len(calificaciones)
    return promedio

ultimo_id_calificacion = 0  # Variable global para llevar el conteo

@app.route('/api/calificar', methods=['POST'])
def api_calificar():
    global ultimo_id_calificacion

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON"}), 400

    try:
        id_lugar = int(data.get("id_lugar"))
        puntaje = float(data.get("puntaje"))
    except (ValueError, TypeError):
        return jsonify({"error": "id_lugar debe ser entero y puntaje numérico"}), 400

    comentario = data.get("comentario", "")

    lugar = obtener_lugar_por_id(id_lugar)
    if lugar is None:
        return jsonify({"error": "Lugar no encontrado"}), 404

    # Actualizar promedio y cantidad de calificaciones
    promedio_actual = getattr(lugar, 'calificacion', 0.0)
    cantidad_actual = getattr(lugar, 'cantidad_calificaciones', 0)

    nuevo_promedio = (promedio_actual * cantidad_actual + puntaje) / (cantidad_actual + 1)
    lugar.calificacion = nuevo_promedio
    lugar.cantidad_calificaciones = cantidad_actual + 1

    guardar_lugar(lugar)

    # Incrementar ID secuencial y crear calificación nueva
    ultimo_id_calificacion += 1
    id_calificacion = ultimo_id_calificacion

    calif = Calificacion(id_calificacion, id_lugar, puntaje, comentario)
    insertar_calificacion_en_arbol(arbol_calificaciones, calif)
    guardar_calificacion_csv(calif)

    return jsonify({"mensaje": "Calificación registrada", "nuevo_promedio": nuevo_promedio}), 200


@app.route('/api/calificaciones/<int:id_lugar>', methods=['GET'])
def api_obtener_calificaciones(id_lugar):
    nodo_calificaciones = arbol_calificaciones.buscar(id_lugar)
    if not nodo_calificaciones:
        return jsonify({"id_lugar": id_lugar, "promedio": 0, "calificaciones": []})

    return jsonify({
        "id_lugar": nodo_calificaciones.id_lugar,
        "promedio": nodo_calificaciones.promedio(),
        "calificaciones": [c.to_dict() for c in nodo_calificaciones.calificaciones.recorrer()]
    })



#API's PARA LUGARES
#API PARA SOLAMENTE OBTENER UN LUGAR EN ESPECIFICO
@app.route('/api/lugar', methods=['GET'])
def api_lugar():
    nombre = request.args.get('nombre')
    if not nombre:
        return jsonify({"error": "Falta el parámetro 'nombre'"}), 400

    lugar = arbol_lugares.buscar_por_nombre(nombre)
    if not lugar:
        return jsonify({"error": "Lugar no encontrado"}), 404

    lugar_dict = {
        "id" : lugar.id,
        "nombre": lugar.nombre,
        "direccion": lugar.direccion,
        "municipio": lugar.municipio,
        "departamento": lugar.departamento,
        "tipo": lugar.tipo,
        "calificacion": getattr(lugar, "calificacion", "N/A"),
        "latitud": getattr(lugar, "latitud", None),
        "longitud": getattr(lugar, "longitud", None),
        "precio" :getattr(lugar, "precio", None),
        "tiempo" :getattr(lugar, "tiempo", None)
    }
    return jsonify({"lugar": lugar_dict})

#API para cargar los lugares desde el CSV
@app.route('/api/lugares', methods=['GET'])
def obtener_lugares():
    try:
        # Siempre devolvemos solo lugares (sin hospedajes)
        lugares = []
        for lugar in arbol_lugares.obtener_lugares():
            lugares.append({
                "id": lugar.id,
                "nombre": lugar.nombre,
                "tipo": lugar.tipo,
                "latitud": lugar.latitud,
                "longitud": lugar.longitud,
                "municipio": lugar.municipio,
                "departamento": lugar.departamento,
                "calificacion": lugar.calificacion,
                "direccion": lugar.direccion,
                "precio" : lugar.precio,
                "tiempo" : lugar.tiempo
            })

        return jsonify({"lugares": lugares})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#API para registrar lugar en el archivo CSV
@app.route('/api/registrar-lugar', methods=['POST'])
def registrar_lugar():
    datos = request.get_json()

    try:
        tiempo = float(datos.get('tiempo_estadia', 0) or 0)
        precio = float(datos.get('precio', 0) or 0)

        nuevo_lugar = Lugar(
            id=obtener_siguiente_id(),
            departamento=datos['departamento'],
            municipio=datos['municipio'],
            nombre=datos['nombre'],
            tipo=datos['tipo'],
            direccion=datos['direccion'],
            latitud=float(datos['latitud']),
            longitud=float(datos['longitud']),
            calificacion=0.0,
            tiempo=tiempo,
            precio=precio
        )

    except (KeyError, ValueError) as e:
        return jsonify({'error': 'Datos inválidos o faltantes', 'detalle': str(e)}), 400

    guardar_lugar_en_csv(nuevo_lugar, 'data/datos.csv')

    arbol_lugares.insertar(nuevo_lugar)

    return jsonify({'mensaje': 'Lugar registrado con éxito', 'id': nuevo_lugar.id}), 201


#API's PARA HOSPEDAJES
@app.route('/api/registrar-hospedaje', methods=['POST'])
def registrar_hospedaje():
    datos = request.get_json()

    try:
        tiempo = float(datos.get('tiempo_estadia', 0) or 0)
        precio = float(datos.get('precio', 0) or 0)

        nuevo_lugar = Lugar(
            id=obtener_siguiente_id(),
            departamento=datos['departamento'],
            municipio=datos['municipio'],
            nombre=datos['nombre'],
            tipo=datos['tipo'],
            direccion=datos['direccion'],
            latitud=float(datos['latitud']),
            longitud=float(datos['longitud']),
            calificacion=0.0,
            tiempo=tiempo,
            precio=precio
        )
    except (KeyError, ValueError) as e:
        return jsonify({'error': 'Datos inválidos o faltantes', 'detalle': str(e)}), 400

    guardar_lugar_en_csv(nuevo_lugar, 'data/datos.csv')

    arbol_hospedaje.insertar(nuevo_lugar)

    return jsonify({'mensaje': 'Lugar registrado con éxito', 'id': nuevo_lugar.id}), 201

@app.route('/api/hospedajes', methods=['GET'])#API obtener hospedajes
def obtener_hospedajes():
    try:
        hospedajes = [{
            "id": hospedaje.id,
            "nombre": hospedaje.nombre,
            "tipo": hospedaje.tipo,
            "latitud": hospedaje.latitud,
            "longitud": hospedaje.longitud,
            "municipio": hospedaje.municipio,
            "departamento": hospedaje.departamento,
            "calificacion": hospedaje.calificacion,
            "direccion": hospedaje.direccion,
            "precio" : hospedaje.precio
        } for hospedaje in arbol_hospedaje.obtener_lugares()]
        return jsonify({"hospedajes": hospedajes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    #API PARA SOLAMENTE OBTENER UN LUGAR EN ESPECIFICO
@app.route('/api/hospedaje', methods=['GET'])
def api_hospedaje():
    nombre = request.args.get('nombre')
    if not nombre:
        return jsonify({"error": "Falta el parámetro 'nombre'"}), 400

    lugar = arbol_hospedaje.buscar_por_nombre(nombre)
    if not lugar:
        return jsonify({"error": "Lugar no encontrado"}), 404

    lugar_dict = {
        "nombre": lugar.nombre,
        "direccion": lugar.direccion,
        "municipio": lugar.municipio,
        "departamento": lugar.departamento,
        "tipo": lugar.tipo,
        "calificacion": getattr(lugar, "calificacion", "N/A"),
        "latitud": getattr(lugar, "latitud", None),
        "longitud": getattr(lugar, "longitud", None),
        "precio" : getattr(lugar, "precio", None),
    }
    return jsonify({"lugar": lugar_dict})

#API RECOMENDACIONES LUGARES

def extraer_precio(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    if not isinstance(valor, str):
        return 0.0
    valor = valor.strip().lower()
    if "gratis" in valor:
        return 0.0
    numeros = re.findall(r'\d+\.?\d*', valor)
    return float(numeros[0]) if numeros else 0.0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distancia = R * c
    return distancia

def estimar_tiempo_traslado_simple(origen, destino, velocidad_kmh=40):
    try:
        lat1 = float(getattr(origen, "latitud"))
        lon1 = float(getattr(origen, "longitud"))
        lat2 = float(getattr(destino, "latitud"))
        lon2 = float(getattr(destino, "longitud"))
    except (TypeError, ValueError, AttributeError):
        return 0.0

    distancia_km = haversine(lat1, lon1, lat2, lon2)
    tiempo_horas = distancia_km / velocidad_kmh
    return max(tiempo_horas, 0.0)

async def estimar_tiempo_traslado_async(session, origen, destino):
    try:
        lat1 = float(getattr(origen, "latitud", None))
        lon1 = float(getattr(origen, "longitud", None))
        lat2 = float(getattr(destino, "latitud", None))
        lon2 = float(getattr(destino, "longitud", None))
    except (TypeError, ValueError):
        return 0.0

    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    key_cache = (lat1, lon1, lat2, lon2)
    if key_cache in cache_tiempos_traslado:
        return cache_tiempos_traslado[key_cache]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{lat1},{lon1}",
        "destinations": f"{lat2},{lon2}",
        "key": API_KEY,
        "units": "metric"
    }

    try:
        async with session.get(url, params=params, timeout=10) as resp:
            data = await resp.json()
            if data.get('status') == 'OK':
                elemento = data['rows'][0]['elements'][0]
                if elemento.get('status') == 'OK':
                    duracion_s = elemento['duration']['value']
                    horas = duracion_s / 3600
                    cache_tiempos_traslado[key_cache] = horas
                    return max(horas, 0.0)
    except Exception as e:
        print(f"Error Google Maps API: {e}")
    return 0.0

def calcular_puntaje(lugar, precio, tiempo_total):
    calificacion = float(getattr(lugar, 'calificacion', 0) or 0)
    max_precio = 100
    max_tiempo = 8
    precio_norm = max(0, min(1, 1 - precio / max_precio))  
    tiempo_norm = max(0, min(1, 1 - tiempo_total / max_tiempo))  
    calif_norm = max(0, min(1, calificacion / 5))

    peso_calif = 0.5
    peso_precio = 0.25
    peso_tiempo = 0.25

    puntaje = calif_norm * peso_calif + precio_norm * peso_precio + tiempo_norm * peso_tiempo
    return puntaje

def formatear_tiempo(tiempo_horas):
    if tiempo_horas < 1:
        minutos = tiempo_horas * 60
        return f"{minutos:.1f} mins"
    else:
        return f"{tiempo_horas:.2f} hrs"

@app.route('/api/recomendaciones')
def api_recomendaciones():
    nombre = request.args.get('nombre')
    if not nombre:
        return jsonify({"error": "Falta el parámetro 'nombre'"}), 400
    
    lugar = arbol_lugares.buscar_por_nombre(nombre)
    if not lugar:
        return jsonify({"error": "Lugar no encontrado"}), 404

    try:
        presupuesto = float(request.args.get('presupuesto', 1e10))
    except ValueError:
        presupuesto = 1e10

    try:
        tiempo_max_diario = float(request.args.get('tiempo_max_diario', 8))
    except ValueError:
        tiempo_max_diario = 8

    departamento = lugar.departamento.strip().lower()

    recomendaciones = [
        l for l in arbol_lugares.obtener_lugares()
        if (
            l.departamento.strip().lower() == departamento and 
            l.nombre != lugar.nombre and 
            getattr(l, "latitud", None) is not None and
            getattr(l, "longitud", None) is not None
        )
    ]

    usar_api_google = False  # Cambiar a True para usar API Google Distance Matrix (No utilizada por el momento)

    async def filtrar_y_calcular():
        if usar_api_google:
            async with aiohttp.ClientSession() as session:
                resultados = []
                for l in recomendaciones:
                    precio = extraer_precio(getattr(l, "precio", 0))
                    try:
                        tiempo_estadia = float(getattr(l, "tiempo", 0))
                    except (ValueError, TypeError):
                        tiempo_estadia = 0
                    
                    tiempo_traslado = await estimar_tiempo_traslado_async(session, lugar, l) or 0.0
                    tiempo_total = tiempo_estadia + tiempo_traslado

                    if precio <= presupuesto and tiempo_total <= tiempo_max_diario:
                        puntaje = calcular_puntaje(l, precio, tiempo_total)
                        resultados.append((l, precio, tiempo_estadia, tiempo_traslado, puntaje))

                resultados.sort(key=lambda x: x[4], reverse=True)
                return resultados[:5]
        else:
            resultados = []
            for l in recomendaciones:
                precio = extraer_precio(getattr(l, "precio", 0))
                try:
                    tiempo_estadia = float(getattr(l, "tiempo", 0))
                except (ValueError, TypeError):
                    tiempo_estadia = 0
                
                tiempo_traslado = estimar_tiempo_traslado_simple(lugar, l) or 0.0
                tiempo_total = tiempo_estadia + tiempo_traslado

                if precio <= presupuesto and tiempo_total <= tiempo_max_diario:
                    puntaje = calcular_puntaje(l, precio, tiempo_total)
                    resultados.append((l, precio, tiempo_estadia, tiempo_traslado, puntaje))

            resultados.sort(key=lambda x: x[4], reverse=True)
            return resultados[:5]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultados_filtrados = loop.run_until_complete(filtrar_y_calcular())
    loop.close()

    lista_recomendaciones = []
    for r, precio, t_estadia, t_traslado, puntaje in resultados_filtrados:
        lista_recomendaciones.append({
            "nombre": r.nombre,
            "direccion": r.direccion,
            "municipio": r.municipio,
            "departamento": r.departamento,
            "latitud": float(getattr(r, "latitud", 0) or 0),
            "longitud": float(getattr(r, "longitud", 0) or 0),
            "calificacion": float(getattr(r, "calificacion", 0) or 0),
            "precio": precio,
            "tiempo_estadia": t_estadia,
            "tiempo_traslado": t_traslado,
            "tiempo_traslado_str": formatear_tiempo(t_traslado),
            "puntaje": puntaje
        })
    
    return jsonify({"recomendaciones": lista_recomendaciones})

@app.route('/api/generar_grafo', methods=['POST'])
def api_generar_grafo():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se recibió data JSON'}), 400

    nodos = data.get('nodos')
    aristas = data.get('aristas')
    id_grafo = data.get('id')

    if nodos is None or aristas is None or id_grafo is None:
        return jsonify({'error': 'Faltan campos nodos, aristas o id'}), 400

    if not isinstance(nodos, list) or not isinstance(aristas, list):
        return jsonify({'error': 'Los campos nodos y aristas deben ser listas'}), 400

    try:
        ruta = generar_grafo_ponderado(nodos, aristas, id_grafo)
        return jsonify({'exito': True, 'mensaje': 'Grafo generado', 'rutaArchivo': ruta})
    except Exception as e:
        return jsonify({'exito': False, 'error': f'Error interno: {str(e)}'}), 500
    
#PAGINAS WEB
@app.route('/') #PAGINA PRINCIPAL
def home():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('index.html', css_path=css_path, js_path=js_path, ocultar=False)

@app.route('/cargar')#PAGINA PARA AGREGAR REGISTROS A CSV
def cargar():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    cargar = url_for('static', filename='js/cargar.js')

    tipo = request.args.get('tipo')
    if tipo == 'hospedaje':
        return redirect(url_for('cargar_hospedaje'))
    elif tipo == 'lugar':
        return redirect(url_for('cargar_lugar'))
    else:
        return render_template('cargar.html', css_path=css_path, js_path=js_path, cargar=cargar)

@app.route('/cargar/lugar')#PAGINA PARA AGREGAR LUGARES
def cargar_lugar():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    cargar = url_for('static', filename='js/cargar.js')

    return render_template('cargar_lugar.html', css_path=css_path, js_path=js_path, cargar=cargar)

@app.route('/lugares') #PAGINA PARA MOSTRAR LOS LUGARES
def lugares():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    lugaresjs = url_for('static', filename='js/lugar.js')

    lugares_data = arbol_lugares.obtener_lugares()

    return render_template(
        'index.html',
        lugares=lugares_data,
        css_path=css_path,
        js_path=js_path,
        lugaresjs=lugaresjs,
        ocultar=False
    )

def render_lugar_detalle(nombre):
    if not nombre:
        return "Falta el nombre del lugar", 400

    lugar = arbol_lugares.buscar_por_nombre(nombre)
    if not lugar:
        return "Lugar no encontrado", 404

    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    mapa = url_for('static', filename='js/mapa.js')
    lugarjs = url_for('static', filename='js/lugar.js')
    detalle = url_for('static', filename='js/detalle_lugar.js')

    return render_template(
        'lugardetalle.html',
        lugar=lugar,
        css_path=css_path,
        js_path=js_path,
        lugarjs=lugarjs,
        detalle=detalle,
        mapa=mapa,
        ocultar = True
    )

@app.route('/lugares/detalle')#PAGINA PARA MOSTRAR UN LUGAR CON TODOS SUS DETALLES
def lugar_detalle():
    try:
        nombre = request.args.get('nombre')
        return render_lugar_detalle(nombre)
    except Exception as e:
        return f"Error interno del servidor: {e}", 500


@app.route('/lugares/filtro/detalle')#PAGINA PARA MOSTRAR EL LUGAR CON DETALLES DESDE LA PAGINA FILTRO
def lugar_detalle_filtro():
    try:
        nombre = request.args.get('nombre')
        presupuesto = request.args.get('presupuesto')
        return render_lugar_detalle(nombre, presupuesto)
    except Exception as e:
        return f"Error interno del servidor: {e}", 500


@app.route('/lugares/filtro')
def lugares_filtro():
    try:
        busqueda = request.args.get('busqueda', '').strip().lower()
        presupuesto_str = request.args.get('presupuesto', '').strip()

        presupuesto = None
        if presupuesto_str != '':
            try:
                presupuesto = float(presupuesto_str)
            except ValueError:
                presupuesto = None

        lugares = arbol_lugares.obtener_lugares()

        if busqueda:
            lugares = [
                lugar for lugar in lugares
                if busqueda in lugar.departamento.strip().lower()
                or busqueda in lugar.nombre.strip().lower()
                or busqueda in lugar.municipio.strip().lower()
            ]

        if presupuesto is not None:
            lugares = [
                lugar for lugar in lugares
                if lugar.precio <= presupuesto
            ]

        return render_template(
            'lugares_filtro.html',
            lugares=lugares,
            busqueda=busqueda,
            presupuesto=presupuesto,
        )
    except Exception as e:
        return f"Error interno del servidor: {e}", 500


#HOSPEDAJES
@app.route('/hospedajes') #PAGINA PARA MOSTRAR LOS HOSPEDAJES
def hospedajes():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    jsH = url_for('static', filename='js/hospedaje.js')

    hospedajes_data = arbol_hospedaje.obtener_lugares()

    return render_template(
        'hospedajes.html',
        hospedajes=hospedajes_data,  
        css_path=css_path,
        js_path=js_path,
        jsH=jsH,
        ocultar=False
    )

@app.route('/cargar/hospedaje')#PAGINA PARA AGREGAR HOSPEDAJES
def cargar_hospedaje():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    cargar = url_for('static', filename='js/cargar.js')

    return render_template('cargar_hospedaje.html', css_path=css_path, js_path=js_path, cargar=cargar, ocultar=True)

def render_hospedaje_detalle(nombre):
    if not nombre:
        return "Falta el nombre del hospedaje", 400

    hospedaje = arbol_hospedaje.buscar_por_nombre(nombre)
    if not hospedaje:
        return "Hospedaje no encontrado", 404

    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    mapa = url_for('static', filename='js/mapa.js')
    jsH = url_for('static', filename='js/hospedaje.js')
    detalle = url_for('static', filename='js/detalle_hospedaje.js')

    return render_template(
        'hospedajedetalle.html',
        hospedaje=hospedaje,
        css_path=css_path,
        js_path=js_path,
        jsH=jsH,
        detalle=detalle,
        mapa=mapa,
        ocultar = True
    )

@app.route('/hospedajes/detalle')
def hospedaje_detalle():
    try:
        nombre = request.args.get('nombre')
        return render_hospedaje_detalle(nombre)
    except Exception as e:
        return f"Error interno del servidor: {e}", 500


@app.route('/hospedajes/filtro/detalle')
def hospedaje_detalle_filtro():
    try:
        nombre = request.args.get('nombre')
        return render_hospedaje_detalle(nombre)
    except Exception as e:
        return f"Error interno del servidor: {e}", 500

@app.route('/hospedajes/filtro')
def hospedajes_filtro():
    try:
        busqueda = request.args.get('busqueda', '').strip().lower()
        presupuesto_str = request.args.get('presupuesto', '').strip()

        presupuesto = None
        if presupuesto_str != '':
            try:
                presupuesto = float(presupuesto_str)
            except ValueError:
                presupuesto = None  

        hospedajes = arbol_hospedaje.obtener_lugares()

        if busqueda:
            hospedajes = [
                h for h in hospedajes
                if busqueda in h.departamento.strip().lower()
                or busqueda in h.nombre.strip().lower()
                or busqueda in h.municipio.strip().lower()
                or busqueda in h.tipo.strip().lower()
            ]

        if presupuesto is not None:
            hospedajes = [
                h for h in hospedajes
                if h.precio <= presupuesto
            ]

        css_path = url_for('static', filename='css/app.css')
        js_path = url_for('static', filename='js/scripts.js')
        jsH = url_for('static', filename='js/hospedaje.js')
        detalle = url_for('static', filename='js/detalle_hospedaje.js')
        ocultar = False

        return render_template(
            'hospedajes_filtro.html',
            hospedajes=hospedajes,
            busqueda=busqueda,
            presupuesto=presupuesto,
            css_path=css_path,
            js_path=js_path,
            jsH=jsH,
            detalle=detalle,
            ocultar=ocultar
        )

    except Exception as e:
        return f"Error interno del servidor: {e}", 500



# API PARA RECOMENDACIONES DE HOSPEDAJES
@app.route('/api/recomendaciones_hospedajes')
def api_recomendaciones_hospedajes():
    nombre = request.args.get('nombre')
    if not nombre:
        return {"error": "Falta el parámetro 'nombre'"}, 400
    
    hospedaje = arbol_hospedaje.buscar_por_nombre(nombre)
    if not hospedaje:
        return {"error": "Hospedaje no encontrado"}, 404
    
    departamento = hospedaje.departamento.strip().lower()
    
    recomendaciones = [
        h for h in arbol_hospedaje.obtener_lugares()
        if h.departamento.strip().lower() == departamento and h.nombre != hospedaje.nombre
    ]
    
    recomendaciones.sort(key=lambda x: getattr(x, 'calificacion', 0), reverse=True)
    recomendaciones = recomendaciones[:5]
    
    lista_recomendaciones = []
    for r in recomendaciones:
        lista_recomendaciones.append({
            "nombre": r.nombre,
            "direccion": r.direccion,
            "municipio": r.municipio,
            "departamento": r.departamento,
            "latitud": getattr(r, "latitud", None),
            "longitud": getattr(r, "longitud", None),
            "calificacion": getattr(r, "calificacion", "N/A"),
            "precio" :getattr (r, "precio", None)
        })
    return {"recomendaciones": lista_recomendaciones}


if __name__ == "__main__":
    app.run(debug=True)
