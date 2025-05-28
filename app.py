from flask import Flask, render_template, url_for, request, jsonify
from flask import Flask, request, render_template, url_for, Response
import json
from backend import arbolB
from backend.arbolB import BTree
from backend.carga_csv import cargar_lugares_csv, cargar_calificaciones_csv
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
from backend.modelos.GrafoPonderado import GrafoPonderado  # Importar clase GrafoPonderado para el manejo de rutas

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Forzar recarga de plantillas

#Diccionario para crear arboles segun el tipo de actividad
arbol_lugares = BTree(grado=5)     # Para turismo, comida, entretenimiento
arbol_hospedaje = BTree(grado=5)  # Para hospedaje
grafo = GrafoPonderado()  # Grafo para rutas ponderadas


#Carga automatica del CSV al iniciar el servidor
try:
    with open('data/datos.csv', 'rb') as archivo_csv:
        cargar_lugares_csv(archivo_csv, arbol_lugares, arbol_hospedaje)
        print("Lugares y hospedajes cargados correctamente")
        
    # Exportar árboles justo después de cargar
    UtilidadesGrafo.exportarArbol(arbol_lugares, "arbol_lugares")
    UtilidadesGrafo.exportarArbol(arbol_hospedaje, "arbol_hospedajes")

except Exception as e:
    print(f"Error al cargar: {e}")


#visualización carga lugares
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
            for lugar in arbol_lugares.obtener_lugares():
                grafo.agregar_vertice(lugar.id)
        

        return Response(json.dumps({"lugares": lugares}, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), content_type="application/json", status=500)


# Rutas web
@app.route('/')  # Página completa
def home():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('index.html', css_path=css_path, js_path=js_path, ocultar=False)

@app.route('/cargar')  # Página completa
def cargar():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('cargar.html', css_path=css_path, js_path=js_path, ocultar=True)

@app.route('/lugares')  # Página completa
def lugares():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    lugaresjs = url_for('static', filename='js/lugares.js')

    # Obtener lugares desde el árbol
    lugares_data = []

    for lugar in arbol_lugares.obtener_lugares():
        lugares_data.append(lugar)

    return render_template(
        'lugares.html',
        lugares=lugares_data,
        css_path=css_path,
        js_path=js_path,
        lugaresjs = lugaresjs,
        ocultar=False
    )

@app.route('/hospedajes')  # Página completa
def hospedajes():
    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    return render_template('hospedajes.html', css_path=css_path, js_path=js_path, ocultar=False)


# API: Cargar calificaciones desde archivo CSV
@app.route('/api/cargar-calificaciones', methods=['POST'])
def cargar_calificaciones():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400
    archivo = request.files['archivo']
    try:
        cargar_calificaciones_csv(archivo, arbolB)
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
    app.run(host="127.0.0.1", port=5000, debug=True)
