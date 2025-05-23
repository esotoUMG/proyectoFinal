from flask import Flask, render_template, url_for
from backend.arbolB import BTree
from backend.carga_csv import cargar_lugares_csv, cargar_calificaciones_csv

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Forzar recarga de plantillas

# Instancia global del Árbol B
arbol = BTree(grado=3)

@app.route('/')
def home():
    js1_ = url_for('static', filename='js/scripts.js')
    css_ = url_for('static', filename='css/app.css')
    main = url_for('static', filename='react/main.jsx')
    return render_template('index.html', css_path=css_, js_path1=js1_, react = main)

# API: Cargar lugares desde archivo CSV
@app.route('/api/cargar-lugares', methods=['POST'])
def cargar_lugares():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo.'}), 400
    archivo = request.files['archivo']
    try:
        cargar_lugares_csv(archivo, arbol)
        return jsonify({'mensaje': 'Lugares cargados correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API: Cargar calificaciones desde archivo CSV
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

if __name__ == "__main__":
    app.run(debug=True)
