from flask import Flask, render_template, url_for, request, jsonify, Response, redirect
import json, os, csv
from backend.arbolB import BTree
from backend.carga_csv import cargar_lugares_csv, cargar_calificaciones_csv, guardar_lugar_en_csv, guardar_calificacion_en_csv
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
from backend.modelos.GrafoPonderado import GrafoPonderado  # Importar clase GrafoPonderado para el manejo de rutas
from backend.modelos.lugar import Lugar

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Recarga automática de plantillas

#Diccionario para crear arboles segun el tipo de actividad
arbol_lugares = BTree(grado=5)     # Para turismo, comida, entretenimiento
arbol_hospedaje = BTree(grado=5)  # Para hospedaje


#Carga automatica del CSV al iniciar el servidor
try:
    with open('data/datos.csv', 'rb') as archivo_csv:
        cargar_lugares_csv(archivo_csv, arbol_lugares, arbol_hospedaje)
        print("Lugares y hospedajes cargados correctamente")

    UtilidadesGrafo.exportarArbol(arbol_lugares, "arbol_lugares")
    UtilidadesGrafo.exportarArbol(arbol_hospedaje, "arbol_hospedajes")

    print(f"Lugares cargados: {len(arbol_lugares.obtener_lugares())}")
    print(f"Hospedajes cargados: {len(arbol_hospedaje.obtener_lugares())}")

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

#API mostrar recomendaciones
@app.route('/api/recomendaciones')
def api_recomendaciones():
    nombre = request.args.get('nombre')
    if not nombre:
        return {"error": "Falta el parámetro 'nombre'"}, 400
    
    lugar = arbol_lugares.buscar_por_nombre(nombre)
    if not lugar:
        return {"error": "Lugar no encontrado"}, 404
    
    departamento = lugar.departamento.strip().lower()
    
    # Obtener lugares en el mismo departamento, excepto el actual
    recomendaciones = [
        l for l in arbol_lugares.obtener_lugares()
        if l.departamento.strip().lower() == departamento and l.nombre != lugar.nombre
    ]
    
    # Opcional: ordenar recomendaciones por calificación descendente (si tienes atributo calificacion numérica)
    recomendaciones.sort(key=lambda x: getattr(x, 'calificacion', 0), reverse=True)
    
    # Tomar máximo 5 recomendaciones
    recomendaciones = recomendaciones[:5]
    
    # Formatear para JSON: devolver solo los campos que usas en JS
    lista_recomendaciones = []
    for r in recomendaciones:
        lista_recomendaciones.append({
            "nombre": r.nombre,
            "direccion": r.direccion,
            "municipio": r.municipio,
            "departamento": r.departamento,
            "latitud": getattr(r, "latitud", None),   
            "longitud": getattr(r, "longitud", None) ,
            "calificacion": getattr(r, "calificacion", "N/A"),
            "precio": getattr(r, "precio", None),
            "tiempo" :getattr(lugar, "tiempo", None)
        })
    
    return {"recomendaciones": lista_recomendaciones}



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
        return render_lugar_detalle(nombre)
    except Exception as e:
        return f"Error interno del servidor: {e}", 500


@app.route('/lugares/filtro')  # PAGINA PARA MOSTRAR LOS LUGARES SEGUN EL FILTRO
def lugares_filtro():
    try:
        tipo = request.args.get('tipo', '').strip().lower()
        departamento = request.args.get('departamento', '').strip().lower()

        tipos_validos = ['turismo', 'comida', 'entretenimiento']

        if tipo not in tipos_validos:
            # Redirigir a un tipo válido por defecto, por ejemplo "turismo"
            return redirect(url_for('lugares_filtro', tipo='turismo'))

        if departamento == 'todo' or departamento == '':
            departamento = None

        if departamento:
            lugares_filtrados = [
                lugar for lugar in arbol_lugares.obtener_lugares()
                if lugar.tipo.strip().lower() == tipo and lugar.departamento.strip().lower() == departamento
            ]
        else:
            lugares_filtrados = [
                lugar for lugar in arbol_lugares.obtener_lugares()
                if lugar.tipo.strip().lower() == tipo
            ]

        css_path = url_for('static', filename='css/app.css')
        js_path = url_for('static', filename='js/scripts.js')
        lugarjs = url_for('static', filename='js/lugar.js')
        detalle = url_for('static', filename='js/detalle_lugar.js')

        return render_template(
            'lugares_filtro.html',
            lugares=lugares_filtrados,
            tipo=tipo,
            departamento=departamento if departamento else "Todos",
            css_path=css_path,
            js_path=js_path,
            lugarjs=lugarjs,
            detalle=detalle,
            ocultar = False
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
        tipo = request.args.get('tipo')
        departamento = request.args.get('departamento')

        if not tipo or tipo.strip() == "":
            return redirect(url_for('hospedajes_filtro', tipo='hotel'))

        tipo = tipo.strip().lower()
        departamento = departamento.strip().lower() if departamento else None

        tipos_validos = ['hotel', 'hostal', 'apartamento']  # ejemplo, ajusta según tus tipos

        if tipo not in tipos_validos:
            return redirect(url_for('hospedajes_filtro', tipo='hotel'))

        if departamento == 'todo':
            departamento = None

        if departamento:
            hospedajes_filtrados = [
                lugar for lugar in arbol_hospedaje.obtener_lugares()
                if lugar.tipo.strip().lower() == tipo and lugar.departamento.strip().lower() == departamento
            ]
        else:
            hospedajes_filtrados = [
                lugar for lugar in arbol_hospedaje.obtener_lugares()
                if lugar.tipo.strip().lower() == tipo
            ]

        css_path = url_for('static', filename='css/app.css')
        js_path = url_for('static', filename='js/scripts.js')
        jsH = url_for('static', filename='js/hospedaje.js')
        detalle = url_for('static', filename='js/detalle_hospedaje.js',
        ocultar = False)

        return render_template(
            'hospedajes_filtro.html',
            hospedajes=hospedajes_filtrados,
            tipo=tipo,
            departamento=departamento if departamento else "Todos",
            css_path=css_path,
            js_path=js_path,
            jsH=jsH,
            detalle=detalle
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

@app.route('/detalle/<int:idx>')
def detalle(idx):
    return render_template(
        'detalle.html',
        detalle=url_for('static', filename='js/detalle.js'),
        mapa=url_for('static', filename='js/mapa.js')
    )

# @app.route('/api/cargar-calificaciones', methods=['POST'])
# def cargar_calificaciones():
#     if 'archivo' not in request.files:
#         return jsonify({'error': 'No se envió ningún archivo.'}), 400

#     archivo = request.files['archivo']
#     try:
#         cargar_calificaciones_csv(archivo, arbol)
#         return jsonify({'mensaje': 'Calificaciones cargadas correctamente.'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/rutas', methods=['GET'])
# def obtener_rutas():
#     origen = request.args.get('origen')
#     if not origen:
#         return jsonify({'error': 'Parámetro "origen" requerido'}), 400
#     try:
#         distancias = grafo.dijkstra(origen)
#         return jsonify({'distancias': distancias}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
# # @app.route("/grafo")
# # def mostrar_grafo():
# #     image_path = graficar_grafo(places_graph)
# #     return render_template_string(f"""
# #     <h2>Visualización del Grafo Ponderado</h2>
# #     <img src="{image_path}" alt="Grafo Ponderado">
# #     """)

if __name__ == "__main__":
    app.run(debug=True)
