from flask import Flask, render_template, url_for, request, jsonify, redirect
import json
from backend import arbolB
from backend.arbolB import BTree
from backend.carga_csv import cargar_lugares_csv, cargar_calificaciones_csv
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
from backend.modelos.GrafoPonderado import GrafoPonderado  # Para manejo de rutas

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Recarga automática de plantillas


# ====== Inicialización de estructuras de datos ======
# Árbol B para lugares y hospedajes
arbol_lugares = BTree(grado=5)     # Para turismo, comida, entretenimiento
arbol_hospedaje = BTree(grado=5)  # Para hospedaje

# Carga automática del CSV al iniciar el servidor
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


# ====== APIs para datos ======

# API: Obtener todos los lugares (turismo, comida, entretenimiento)
@app.route('/api/lugares', methods=['GET'])
def obtener_lugares():
    try:
        lugares = [{
            "id": lugar.id,
            "nombre": lugar.nombre,
            "tipo": lugar.tipo,
            "latitud": lugar.latitud,
            "longitud": lugar.longitud,
            "municipio": lugar.municipio,
            "departamento": lugar.departamento,
            "calificacion": lugar.calificacion,
            "direccion": lugar.direccion
        } for lugar in arbol_lugares.obtener_lugares()]

        return jsonify({"lugares": lugares})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API: Obtener todos los hospedajes
@app.route('/api/hospedajes', methods=['GET'])
def obtener_hospedajes():
    try:
        hospedajes = [{
            "id": h.id,
            "nombre": h.nombre,
            "tipo": h.tipo,
            "latitud": h.latitud,
            "longitud": h.longitud,
            "municipio": h.municipio,
            "departamento": h.departamento,
            "calificacion": h.calificacion,
            "direccion": h.direccion
        } for h in arbol_hospedaje.obtener_lugares()]

        return jsonify({"hospedajes": hospedajes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API: Obtener un lugar específico por nombre
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
        "longitud": getattr(lugar, "longitud", None)
    }
    return jsonify({"lugar": lugar_dict})


# API: Obtener un hospedaje específico por nombre
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
        "longitud": getattr(lugar, "longitud", None)
    }
    return jsonify({"lugar": lugar_dict})


# API: Recomendaciones para lugares (en mismo departamento, mejor calificación)
@app.route('/api/recomendaciones')
def api_recomendaciones():
    nombre = request.args.get('nombre')
    if not nombre:
        return {"error": "Falta el parámetro 'nombre'"}, 400

    lugar = arbol_lugares.buscar_por_nombre(nombre)
    if not lugar:
        return {"error": "Lugar no encontrado"}, 404

    departamento = lugar.departamento.strip().lower()

    recomendaciones = [
        l for l in arbol_lugares.obtener_lugares()
        if l.departamento.strip().lower() == departamento and l.nombre != lugar.nombre
    ]
    recomendaciones.sort(key=lambda x: getattr(x, 'calificacion', 0), reverse=True)
    recomendaciones = recomendaciones[:5]

    lista_recomendaciones = [{
        "nombre": r.nombre,
        "direccion": r.direccion,
        "municipio": r.municipio,
        "departamento": r.departamento,
        "latitud": getattr(r, "latitud", None),
        "longitud": getattr(r, "longitud", None),
        "calificacion": getattr(r, "calificacion", "N/A")
    } for r in recomendaciones]

    return {"recomendaciones": lista_recomendaciones}


# API: Recomendaciones para hospedajes (en mismo departamento, mejor calificación)
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

    lista_recomendaciones = [{
        "nombre": r.nombre,
        "direccion": r.direccion,
        "municipio": r.municipio,
        "departamento": r.departamento,
        "latitud": getattr(r, "latitud", None),
        "longitud": getattr(r, "longitud", None),
        "calificacion": getattr(r, "calificacion", "N/A")
    } for r in recomendaciones]

    return {"recomendaciones": lista_recomendaciones}


# API: Cargar calificaciones desde archivo CSV
@app.route('/api/cargar-calificaciones', methods=['POST'])
def cargar_calificaciones():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400

    archivo = request.files['archivo']
    try:
        cargar_calificaciones_csv(archivo, arbol_lugares)
        return jsonify({'mensaje': 'Calificaciones cargadas correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API: Obtener rutas (dijkstra, desde un origen)
@app.route('/api/rutas', methods=['GET'])
def obtener_rutas():
    origen = request.args.get('origen')
    if not origen:
        return jsonify({'error': 'Parámetro "origen" requerido'}), 400
    try:
        distancias = grafo.dijkstra(origen)
        return jsonify({'distancias': distancias}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====== Rutas para páginas web ======

# Página principal
@app.route('/')
def home():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('index.html', css_path=css_path, js_path=js_path, ocultar=False)


# Página para cargar registros a CSV
@app.route('/cargar')
def cargar():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('cargar.html', css_path=css_path, js_path=js_path, ocultar=True)


# Página para mostrar lugares
@app.route('/lugares')
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


# Página para mostrar hospedajes
@app.route('/hospedajes')
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


# Página para filtrar hospedajes por tipo y departamento
@app.route('/hospedajes/filtro')
def hospedajes_filtro():
    try:
        tipo = request.args.get('tipo')
        departamento = request.args.get('departamento')

        if not tipo or tipo.strip() == "":
            return redirect(url_for('hospedajes_filtro', tipo='hotel'))

        tipo = tipo.strip().lower()
        departamento = departamento.strip().lower() if departamento else None

        if departamento and departamento != 'todo':
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
        detalle = url_for('static', filename='js/detalle_hospedaje.js')

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


# ====== Renderizado de detalles ======

# Renderizar detalle de lugar (uso interno)
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
        mapa=mapa
    )


# Página detalle lugar (ruta)
@app.route('/detalle_lugar')
def detalle_lugar():
    nombre = request.args.get('nombre')
    return render_lugar_detalle(nombre)


# Página detalle hospedaje (ruta)
@app.route('/detalle_hospedaje')
def detalle_hospedaje():
    nombre = request.args.get('nombre')
    lugar = arbol_hospedaje.buscar_por_nombre(nombre)
    if not lugar:
        return "Hospedaje no encontrado", 404

    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    lugarjs = url_for('static', filename='js/hospedaje.js')
    detalle = url_for('static', filename='js/detalle_hospedaje.js')

    return render_template(
        'detalle_hospedaje.html',
        lugar=lugar,
        css_path=css_path,
        js_path=js_path,
        lugarjs=lugarjs,
        detalle=detalle
    )


# ====== Main ======
if __name__ == '__main__':
    # Para desarrollo: activar debug y recarga automática
    app.run(debug=True)
