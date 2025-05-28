from flask import Flask, render_template, url_for, request, jsonify, Response
import json
from backend import arbolB
from backend.arbolB import BTree
from backend.carga_csv import cargar_lugares_csv, cargar_calificaciones_csv
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
from backend.modelos.GrafoPonderado import GrafoPonderado  # Importar clase GrafoPonderado para el manejo de rutas

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

@app.route('/api/lugares', methods=['GET'])
def obtener_lugares():
    try:

        tipo = request.args.get('tipo', default='todos')
        lugares = []

        if tipo in ['todos', 'lugares']:
            for lugar in arbol_lugares.obtener_lugares():
                lugares.append({
                    "id": lugar.id,
                    "nombre": lugar.nombre,
                    "tipo": lugar.tipo,
                    "latitud": lugar.latitud,
                    "longitud": lugar.longitud,
                    "calificacion": lugar.calificacion,
                    "direccion": lugar.direccion
                })

        if tipo in ['todos', 'hospedajes']:
            for lugar in arbol_hospedaje.obtener_lugares():
                lugares.append({
                    "id": lugar.id,
                    "nombre": lugar.nombre,
                    "tipo": lugar.tipo,
                    "latitud": lugar.latitud,
                    "longitud": lugar.longitud,
                    "calificacion": lugar.calificacion,
                    "direccion": lugar.direccion
                })
        

        return Response(json.dumps({"lugares": lugares}, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), content_type="application/json", status=500)

@app.route('/api/hospedajes', methods=['GET'])
def obtener_hospedajes():
    try:
        hospedajes = [{
            "id": hospedaje.id,
            "nombre": hospedaje.nombre,
            "tipo": hospedaje.tipo,
            "latitud": hospedaje.latitud,
            "longitud": hospedaje.longitud,
            "calificacion": hospedaje.calificacion,
            "direccion": hospedaje.direccion
        } for hospedaje in arbol_hospedaje.obtener_lugares()]
        return Response(json.dumps({"hospedajes": hospedajes}, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), content_type="application/json", status=500)

@app.route('/')
def home():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('index.html', css_path=css_path, js_path=js_path, ocultar=False)

@app.route('/cargar')
def cargar():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('cargar.html', css_path=css_path, js_path=js_path, ocultar=True)

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

@app.route('/hospedajes')
def hospedajes():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    jsH = url_for('static', filename='js/hospedaje.js')

    hospedajes_data = arbol_hospedaje.obtener_lugares()

    return render_template(
        'hospedajes.html',
        hospedajes=hospedajes_data,  # <-- plural aquí, coincide con el template
        css_path=css_path,
        js_path=js_path,
        jsH=jsH,
        ocultar=False
    )

@app.route('/api/cargar-calificaciones', methods=['POST'])
def cargar_calificaciones():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400

    archivo = request.files['archivo']
    try:
        cargar_calificaciones_csv(archivo, arbol)
        return jsonify({'mensaje': 'Calificaciones cargadas correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == "__main__":
    app.run(host="127.0.0.0", port=5000, debug=True)
