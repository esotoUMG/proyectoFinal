from flask import Flask, render_template_string, request
import csv
import os

app = Flask(__name__)

DATA_CSV = './data/datos.csv'
RATINGS_CSV = './data/ratings.csv'

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

@app.route('/', methods=['GET'])
def index():
    data = load_data()
    ratings_list = load_ratings()
    ratings_summary = aggregate_ratings(ratings_list)

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Calificación y Comentarios por Destino - CSV</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #f0f4f8;
          margin: 0; padding: 20px;
          color: #222;
        }
        h1 {
          text-align: center;
          color: #007acc;
          margin-bottom: 1rem;
        }
        .table-container {
          max-height: 380px;
          overflow-y: auto;
          border: 1px solid #ccc;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          background: white;
          margin-top: 20px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        th, td {
          padding: 12px 15px;
          border: 1px solid #ddd;
          text-align: left;
          vertical-align: middle;
        }
        th {
          background-color: #007acc;
          color: white;
          user-select: none;
          position: sticky;
          top: 0;
          z-index: 2;
        }
        tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        input[type="radio"] {
          transform: scale(1.2);
          cursor: pointer;
        }
        select, textarea {
          font-size: 14px;
          padding: 7px;
          border-radius: 4px;
          margin-left: 10px;
          vertical-align: middle;
          resize: vertical;
          width: 100%;
          box-sizing: border-box;
          font-family: inherit;
        }
        textarea {
          min-height: 80px;
          margin-top: 10px;
        }
        button {
          margin-top: 20px;
          background-color: #007acc;
          color: white;
          border: none;
          padding: 12px 30px;
          border-radius: 5px;
          font-size: 16px;
          cursor: pointer;
          transition: background-color 0.3s ease;
          display: block;
          margin-left: auto;
          margin-right: auto;
        }
        button:disabled {
          background-color: #bbb;
          cursor: not-allowed;
        }
        button:hover:enabled {
          background-color: #005f99;
        }
        .rating-info {
          font-size: 14px;
          color: #555;
          margin-top: 6px;
          cursor: pointer;
          text-decoration: underline;
        }
        label[for="comment"] {
          font-weight: 600;
          display: block;
          margin-top: 20px;
        }
        /* Modal styles */
        .modal {
          display: none; 
          position: fixed;
          z-index: 10;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          overflow: auto;
          background-color: rgb(0,0,0,0.4);
          backdrop-filter: blur(3px);
        }
        .modal-content {
          background-color: #fefefe;
          margin: 10% auto; 
          padding: 20px;
          border: 1px solid #888;
          border-radius: 8px;
          width: 90%;
          max-width: 600px;
          max-height: 70vh;
          overflow-y: auto;
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .close-btn {
          color: #aaa;
          float: right;
          font-size: 28px;
          font-weight: bold;
          cursor: pointer;
        }
        .close-btn:hover,
        .close-btn:focus {
          color: #000;
          text-decoration: none;
        }
        .rating-entry {
          border-bottom: 1px solid #ddd;
          padding: 10px 0;
        }
        .rating-entry:last-child {
          border-bottom: none;
        }
        .rating-value {
          font-weight: bold;
          color: #007acc;
        }
        .comment-text {
          margin-top: 5px;
          white-space: pre-wrap;
          font-style: italic;
          color: #333;
        }
      </style>
    </head>
    <body>
      <h1>Seleccione un destino, califíquelo y deje un comentario</h1>
      {% if data|length == 0 %}
        <p>No se encontraron datos en el archivo CSV.</p>
      {% else %}
      <form method="POST" action="{{ url_for('submit_rating') }}" id="ratingForm">
        <div class="table-container" tabindex="0" role="region" aria-label="Tabla de destinos">
          <table>
            <thead>
              <tr>
                <th>Seleccionar</th>
                {% for col in data[0].keys() %}
                <th>{{ col }}</th>
                {% endfor %}
                <th>Calificación actual</th>
                <th>Ver comentarios</th>
              </tr>
            </thead>
            <tbody>
              {% for row in data %}
              <tr>
                <td style="text-align:center;">
                  <input type="radio" name="selected_row" value="{{ loop.index0 }}" required aria-label="Seleccionar destino número {{ loop.index }}" />
                </td>
                {% for col in row.values() %}
                <td>{{ col }}</td>
                {% endfor %}
                {% set key = loop.index0|string %}
                <td class="rating-info" tabindex="0" role="button" aria-label="Calificación promedio {{ ratings_summary[key].average if key in ratings_summary else 'sin calificación' }}, {{ ratings_summary[key].count if key in ratings_summary else 0 }} evaluaciones" data-key="{{ key }}">
                  {% if key in ratings_summary and ratings_summary[key].average is not none %}
                    {{ "%.2f"|format(ratings_summary[key].average) }} ({{ ratings_summary[key].count }} eval.)
                  {% else %}
                    Sin calificación
                  {% endif %}
                </td>
                <td style="text-align:center;">
                  <button type="button" class="view-comments-btn" data-key="{{ key }}" aria-label="Ver comentarios del destino {{ loop.index }}">🗨️</button>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        <div>
          <label for="rating">Calificación:</label>
          <select name="rating" id="rating" disabled required aria-required="true" aria-describedby="ratingHelp">
            <option value="" selected disabled>Elige</option>
            <option value="1">1 - Muy malo</option>
            <option value="2">2 - Malo</option>
            <option value="3">3 - Regular</option>
            <option value="4">4 - Bueno</option>
            <option value="5">5 - Excelente</option>
          </select>
          <small id="ratingHelp" style="color:#555;">Seleccione una calificación entre 1 y 5.</small>
        </div>
        <div>
          <label for="comment">Comentario:</label>
          <textarea id="comment" name="comment" rows="3" placeholder="Escriba un comentario..." disabled required aria-required="true"></textarea>
        </div>
        <button type="submit" disabled id="submitBtn">Guardar Calificación y Comentario</button>
      </form>

      <!-- Modal for all comments -->
      <div id="commentsModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle" aria-describedby="modalDesc">
        <div class="modal-content">
          <span class="close-btn" id="modalClose" tabindex="0" role="button" aria-label="Cerrar modal">&times;</span>
          <h2 id="modalTitle">Comentarios y Calificaciones</h2>
          <div id="modalBody" tabindex="0" aria-live="polite">
            <!-- Comments and ratings inserted here -->
          </div>
        </div>
      </div>
      {% endif %}

      <script>
      const radios = document.getElementsByName('selected_row');
      const ratingSelect = document.getElementById('rating');
      const commentArea = document.getElementById('comment');
      const submitBtn = document.getElementById('submitBtn');
      const commentsModal = document.getElementById('commentsModal');
      const modalBody = document.getElementById('modalBody');
      const modalClose = document.getElementById('modalClose');

      // Rating and comment input form enable/disable logic
      function updateFormState() {
        const selectedRadio = [...radios].find(r => r.checked);
        const ratingValue = ratingSelect.value.trim();
        const commentValue = commentArea.value.trim();

        if (selectedRadio) {
          ratingSelect.disabled = false;
          commentArea.disabled = false;
          submitBtn.disabled = !(ratingValue !== "" && commentValue !== "");
        } else {
          ratingSelect.disabled = true;
          commentArea.disabled = true;
          submitBtn.disabled = true;
          ratingSelect.value = "";
          commentArea.value = "";
        }
      }

      radios.forEach(radio => {
        radio.addEventListener('change', () => {
          ratingSelect.value = "";
          commentArea.value = "";
          updateFormState();
        });
      });

      ratingSelect.addEventListener('input', updateFormState);
      commentArea.addEventListener('input', updateFormState);

      // Comments modal logic
      const ratingsList = {{ ratings_list|tojson }};
      const data = {{ data|tojson }};
      function createRatingEntry(entry) {
        const div = document.createElement('div');
        div.className = 'rating-entry';
        const rating = document.createElement('div');
        rating.className = 'rating-value';
        rating.textContent = `Calificación: ${entry.rating}`;
        const comment = document.createElement('div');
        comment.className = 'comment-text';
        comment.textContent = entry.comment || "(Sin comentario)";
        div.appendChild(rating);
        div.appendChild(comment);
        return div;
      }

      function openModal(key) {
        modalBody.innerHTML = '';
        const entries = ratingsList.filter(r => r.dest_idx === key);
        if (entries.length === 0) {
          modalBody.textContent = 'No hay comentarios para este destino.';
        } else {
          entries.forEach(entry => {
            modalBody.appendChild(createRatingEntry(entry));
          });
        }
        commentsModal.style.display = 'block';
        modalClose.focus();
      }

      function closeModal() {
        commentsModal.style.display = 'none';
      }

      document.querySelectorAll('.view-comments-btn').forEach(btn => {
        btn.addEventListener('click', e => {
          const key = e.currentTarget.getAttribute('data-key');
          openModal(key);
        });
      });

      modalClose.addEventListener('click', closeModal);
      modalClose.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          closeModal();
        }
      });

      // Close modal on click outside content
      window.addEventListener('click', e => {
        if (e.target === commentsModal) {
          closeModal();
        }
      });

      // Close modal on Esc key
      window.addEventListener('keydown', e => {
        if (e.key === 'Escape' && commentsModal.style.display === 'block') {
          closeModal();
        }
      });
      </script>
    </body>
    </html>
    """
    return render_template_string(html, data=data, ratings_list=ratings_list, ratings_summary=ratings_summary)

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
            'rating': rating_new,
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

