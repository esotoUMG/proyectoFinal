from flask import Flask, render_template_string, request
import csv
import os

app = Flask(__name__)

DATA_CSV = './data/datos.csv'
RATINGS_CSV = './data/calificaciones.csv'

def load_data():
    data = []
    if os.path.exists(DATA_CSV):
        with open(DATA_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    return data

def load_ratings():
    ratings = {}
    if os.path.exists(RATINGS_CSV):
        with open(RATINGS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row['selected_row']
                entry = {'rating': float(row['rating']), 'comment': row['comment']}
                if key in ratings:
                    ratings[key].append(entry)
                else:
                    ratings[key] = [entry]
    return ratings

def save_ratings(ratings):
    with open(RATINGS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['selected_row', 'rating', 'comment']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for selected_row, entries in ratings.items():
            for entry in entries:
                writer.writerow({
                    'selected_row': selected_row,
                    'rating': entry['rating'],
                    'comment': entry['comment']
                })

def calculate_average(rating_list):
    if not rating_list:
        return None
    total = 0
    for entry in rating_list:
        try:
            total += float(entry['rating'])
        except (ValueError, KeyError):
            pass
    avg = total / len(rating_list)
    return round(avg, 2)

@app.route('/', methods=['GET'])
def index():
    data = load_data()
    ratings = load_ratings()
    ratings_summary = {
        k: {'average': calculate_average(v), 'count': len(v)}
        for k, v in ratings.items()
    }

    return render_template_string(TEMPLATE, data=data, ratings=ratings, ratings_summary=ratings_summary)

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = load_data()
    ratings = load_ratings()

    selected_row = request.form.get('selected_row')
    rating_str = request.form.get('rating')
    comment = request.form.get('comment', '').strip()

    if not selected_row or not rating_str or not comment:
        return "Error: Seleccione un destino, calificación y deje un comentario.", 400

    try:
        rating_new = float(rating_str)
    except ValueError:
        return "Calificación inválida.", 400

    if selected_row not in [str(i) for i in range(len(data))]:
        return "Destino seleccionado inválido.", 400

    if selected_row in ratings:
        ratings[selected_row].append({'rating': rating_new, 'comment': comment})
    else:
        ratings[selected_row] = [{'rating': rating_new, 'comment': comment}]

    save_ratings(ratings)

    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Calificación y comentario guardados</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #e6f0ff;
          padding: 50px;
          text-align: center;
          color: #004085;
        }
        a {
          display: inline-block;
          margin-top: 30px;
          background-color: #007acc;
          color: white;
          padding: 12px 25px;
          border-radius: 5px;
          text-decoration: none;
          font-weight: bold;
        }
        a:hover {
          background-color: #005f99;
        }
      </style>
    </head>
    <body>
      <h1>Calificación y comentario guardados con éxito.</h1>
      <a href="/">Volver</a>
    </body>
    </html>
    """

# HTML y JS incrustado como plantilla
TEMPLATE = """ 
<!-- AQUÍ PEGA EL HTML Y JS QUE TENGAS -->
"""

if __name__ == '__main__':
    app.run(debug=True)
