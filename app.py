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


#API LUGARES
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
                "direccion": lugar.direccion
            })

        return jsonify({"lugares": lugares})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#API HOSPEDAJES
@app.route('/api/hospedajes', methods=['GET'])
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
            "direccion": hospedaje.direccion
        } for hospedaje in arbol_hospedaje.obtener_lugares()]
        return jsonify({"hospedajes": hospedajes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    return render_template('cargar.html', css_path=css_path, js_path=js_path, ocultar=True)

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

@app.route('/lugares/filtro') #PAGINA PARA MOSTRAR LOS LUGARES SEGUN EL FILTRO SELECCIONADO
def lugares_filtrados():
    tipo = request.args.get('tipo')
    departamento = request.args.get('departamento')

    if not tipo:
        return "Falta el parámetro 'tipo'", 400

    tipo = tipo.strip().lower()
    departamento = departamento.strip().lower() if departamento else None

    if departamento and departamento != 'todo':
        # Filtra por tipo y departamento
        lugares_filtrados = [
            lugar for lugar in arbol_lugares.obtener_lugares()
            if lugar.tipo.strip().lower() == tipo and lugar.departamento.strip().lower() == departamento
        ]
    else:
        # Solo filtra por tipo (todos los departamentos)
        lugares_filtrados = [
            lugar for lugar in arbol_lugares.obtener_lugares()
            if lugar.tipo.strip().lower() == tipo
        ]

    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    lugaresjs = url_for('static', filename='js/lugar.js')

    return render_template(
        'lugares_filtro.html',
        lugares=lugares_filtrados,
        tipo=tipo,
        departamento=departamento if departamento else "Todos",
        css_path=css_path,
        js_path=js_path,
        lugaresjs=lugaresjs
    )


@app.route('/lugares/detalle')  # Mostrar el lugar con más detalles
def lugar_detalle():
    try:
        nombre = request.args.get('nombre')
        if not nombre:
            return "Falta el nombre del lugar", 400

        lugar = arbol_lugares.buscar_por_nombre(nombre)
        if not lugar:
            return "Lugar no encontrado", 404

        css_path = url_for('static', filename='css/app.css')
        js_path = url_for('static', filename='js/scripts.js')
        lugarjs = url_for('static', filename='js/lugar.js')
        detalle = url_for('static', filename='js/detalle_lugar.js')

        return render_template(
            'lugardetalle.html',
            lugar=lugar,
            css_path=css_path,
            js_path=js_path,
            lugarjs=lugarjs,
            detalle = detalle
        )
    
    except Exception as e:
        return f"Error interno del servidor: {e}", 500



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

@app.route('/hospedajes/filtro') #PAGINA PARA MOSTRAR LOS HOSPEDAJES SEGUN EL FILTRO SELECCIONADO
def hospedajes_filtrados():
    tipo = request.args.get('tipo')
    departamento = request.args.get('departamento')

    if not tipo:
        return "Falta el parámetro 'tipo'", 400

    tipo = tipo.strip().lower()
    departamento = departamento.strip().lower() if departamento else None

    todos_hospedajes = arbol_hospedaje.obtener_lugares()

    if departamento and departamento != 'todo':
        hospedajes_filtrados = [
            h for h in todos_hospedajes
            if h.tipo.strip().lower() == tipo and h.departamento.strip().lower() == departamento
        ]
    else:
        hospedajes_filtrados = [
            h for h in todos_hospedajes
            if h.tipo.strip().lower() == tipo
        ]

    if not hospedajes_filtrados:
        return render_template('hospedajes_filtro.html', 
                               hospedajes=[],
                               tipo=tipo,
                               departamento=departamento if departamento else "Todos",
                               mensaje="No se encontraron hospedajes que coincidan con el filtro.")

    css_path = url_for('static', filename='css/app.css')
    js_path = url_for('static', filename='js/scripts.js')
    hospedajesjs = url_for('static', filename='js/hospedaje.js')

    return render_template(
        'hospedajes_filtro.html',
        hospedajes=hospedajes_filtrados,
        tipo=tipo,
        departamento=departamento if departamento else "Todos",
        css_path=css_path,
        js_path=js_path,
        hospedajesjs=hospedajesjs
    )
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
        "calificacion": getattr(lugar, "calificacion", "N/A")
    }
    return jsonify({"lugar": lugar_dict})



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
            "calificacion": getattr(r, "calificacion", "N/A")
        })
    
    return {"recomendaciones": lista_recomendaciones}


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
# @app.route("/grafo")
# def mostrar_grafo():
#     image_path = graficar_grafo(places_graph)
#     return render_template_string(f"""
#     <h2>Visualización del Grafo Ponderado</h2>
#     <img src="{image_path}" alt="Grafo Ponderado">
#     """)

if __name__ == "__main__":
    app.run(debug=True)
