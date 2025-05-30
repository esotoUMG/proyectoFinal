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
    ratings_list = []
    if os.path.exists(RATINGS_CSV):
        with open(RATINGS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ratings_list.append({
                    'dest_idx': row.get('dest_idx'),
                    'rating': float(row.get('rating',0)),
                    'comment': row.get('comment','')
                })
    return ratings_list

def aggregate_ratings(ratings_list):
    agg = {}
    for r in ratings_list:
        idx = r['dest_idx']
        if idx not in agg:
            agg[idx] = {
                'ratings': [],
                'comments': []
            }
        agg[idx]['ratings'].append(r['rating'])
        agg[idx]['comments'].append(r['comment'])
    # compute average ratings and count
    result = {}
    for idx, vals in agg.items():
        avg = sum(vals['ratings'])/len(vals['ratings']) if vals['ratings'] else None
        result[idx] = {
            'average': round(avg,2) if avg is not None else None,
            'count': len(vals['ratings']),
            'comments': vals['comments']
        }
    return result

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


@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = load_data()

    selected_row = request.form.get('selected_row')
    rating_str = request.form.get('rating')
    comment = request.form.get('comment', '').strip()

    if selected_row is None or rating_str is None or comment == '':
        return "Error: Seleccione un destino, calificación y deje un comentario.", 400
    try:
        rating_new = float(rating_str)
    except ValueError:
        return "Calificación inválida.", 400
    if selected_row not in [str(i) for i in range(len(data))]:
        return "Destino seleccionado inválido.", 400

    file_exists = os.path.exists(RATINGS_CSV)
    with open(RATINGS_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['dest_idx','rating','comment']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'dest_idx': selected_row,
            'rating': rating_str,
            'comment': comment
        })
    
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


if __name__ == '__main__':
    app.run(debug=True)
