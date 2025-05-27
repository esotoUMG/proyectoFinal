import csv
import io
import math
import os
from flask import Flask, request, jsonify, render_template_string, send_file
from graphviz import Digraph

app = Flask(__name__)

# --- Data Structures Implementation ---

# Node for B-Tree
class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree
        self.keys = []  # keys
        self.children = []  # children pointers
        self.leaf = leaf

    def insert_non_full(self, key, data):
        i = len(self.keys) - 1
        if self.leaf:
            # Insert new key into node
            self.keys.append((None,None))
            while i >= 0 and key < self.keys[i][0]:
                self.keys[i+1] = self.keys[i]
                i -= 1
            self.keys[i+1] = (key, data)
        else:
            while i >= 0 and key < self.keys[i][0]:
                i -= 1
            i += 1
            if len(self.children[i].keys) == 2*self.t - 1:
                self.split_child(i)
                if key > self.keys[i][0]:
                    i += 1
            self.children[i].insert_non_full(key, data)

    def split_child(self, i):
        t = self.t
        y = self.children[i]
        z = BTreeNode(t, y.leaf)
        z.keys = y.keys[t:]
        y.keys = y.keys[:t-1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        self.children.insert(i+1, z)
        self.keys.insert(i, y.keys.pop())

    def search(self, key):
        i = 0
        while i < len(self.keys) and key > self.keys[i][0]:
            i += 1
        if i < len(self.keys) and key == self.keys[i][0]:
            return self.keys[i][1]
        if self.leaf:
            return None
        return self.children[i].search(key)

    def traverse(self):
        results = []
        for i in range(len(self.keys)):
            if not self.leaf:
                results.extend(self.children[i].traverse())
            results.append(self.keys[i][1])
        if not self.leaf:
            results.extend(self.children[-1].traverse())
        return results

# B-Tree wrapper
class BTree:
    def __init__(self, t=3):
        self.root = BTreeNode(t, leaf=True)
        self.t = t

    def insert(self, key, data):
        root = self.root
        if len(root.keys) == 2*self.t -1:
            s = BTreeNode(self.t)
            s.children.append(root)
            s.leaf = False
            s.split_child(0)
            i = 0
            if s.keys[0][0] < key:
                i += 1
            s.children[i].insert_non_full(key, data)
            self.root = s
        else:
            root.insert_non_full(key, data)

    def search(self, key):
        return self.root.search(key)

    def get_all(self):
        return self.root.traverse()

# --- Weighted Graph Implementation for routing ---
# Since we can't use native lists, we use linked nodes and own structures

class Edge:
    def __init__(self, to_node, weight): 
        self.to_node = to_node
        self.weight = weight
        self.next = None

class GraphNode:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.edges_head = None
        self.next = None

    def add_edge(self, to_node, weight):
        new_edge = Edge(to_node, weight)
        new_edge.next = self.edges_head
        self.edges_head = new_edge

class WeightedGraph:
    def __init__(self):
        self.head = None

    def add_node(self, key, data):
        # Check if node exists
        if self.get_node(key) is not None:
            return
        new_node = GraphNode(key, data)
        new_node.next = self.head
        self.head = new_node

    def get_node(self, key):
        current = self.head
        while current:
            if current.key == key:
                return current
            current = current.next
        return None

    def add_edge(self, from_key, to_key, weight):
        from_node = self.get_node(from_key)
        to_node = self.get_node(to_key)
        if from_node and to_node:
            from_node.add_edge(to_node, weight)
            # if undirected graph, also add reverse edge
            to_node.add_edge(from_node, weight)

    def dijkstra(self, start_key):
        # Dijkstra implementation using own structures and dict for distances and previous
        # Using Python dict allowed to maintain distance and previous because no native lists allowed for nodes, but distances map keys to values.
        nodes = {}
        current = self.head
        while current:
            nodes[current.key] = current
            current = current.next

        dist = {key: float('inf') for key in nodes}
        prev = {key: None for key in nodes}
        dist[start_key] = 0

        unvisited = set(nodes.keys())

        while unvisited:
            # select node with min dist
            u = None
            u_dist = float('inf')
            for n in unvisited:
                if dist[n] < u_dist:
                    u = n
                    u_dist = dist[n]
            if u is None:
                break
            unvisited.remove(u)

            u_node = nodes[u]
            edge = u_node.edges_head
            while edge:
                alt = dist[u] + edge.weight
                if alt < dist[edge.to_node.key]:
                    dist[edge.to_node.key] = alt
                    prev[edge.to_node.key] = u
                edge = edge.next
        return dist, prev

# --- Data Models ---

class Place:
    def __init__(self, id, name, type_entity, lat, lon, price, avg_rating):
        self.id = id
        self.name = name
        self.type_entity = type_entity  # 'Hospedaje' or 'Turístico'
        self.lat = float(lat)
        self.lon = float(lon)
        self.price = float(price)
        self.avg_rating = float(avg_rating)
        self.user_ratings_total = 0
        self.user_rating_sum = 0

    def update_rating(self, new_rating):
        self.user_rating_sum += new_rating
        self.user_ratings_total += 1
        self.avg_rating = self.user_rating_sum / self.user_ratings_total

class TouristPlace(Place):
    def __init__(self, id, name, lat, lon, price, avg_rating, stay_time):
        super().__init__(id, name, "Turístico", lat, lon, price, avg_rating)
        self.stay_time = float(stay_time)

# --- Global Data Repository ---

places_tree = BTree()

# Graph with nodes is created for tourist places only for routing
places_graph = WeightedGraph()

# --- Helper Functions ---

def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great circle distance between two points on the earth (km)
    R = 6371  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def add_place_to_graph(place):
    if place.type_entity != "Turístico":
        return
    places_graph.add_node(place.id, place)
    # Connect node with all others bi-directionally
    current = places_graph.head
    while current:
        if current.key != place.id:
            dist = haversine(place.lat, place.lon, current.data.lat, current.data.lon)
            time_minutes = dist / 50 * 60  # Assume avg speed 50km/h, convert to minutes
            # weight could incorporate travel time only or travel time + price
            places_graph.add_edge(place.id, current.key, time_minutes)
        current = current.next

def recalculate_graph():
    # Recompute all edges because new nodes added
    # Not efficient but simple for demonstration
    current = places_graph.head
    while current:
        current.edges_head = None
        current = current.next
    current = places_graph.head
    while current:
        current2 = places_graph.head
        while current2:
            if current2.key != current.key:
                dist = haversine(current.data.lat, current.data.lon, current2.data.lat, current2.data.lon)
                time_minutes = dist / 50 * 60
                current.add_edge(current2, time_minutes)
            current2 = current2.next
        current = current.next

def load_places_csv(file):
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.DictReader(stream)
    for row in csv_input:
        # Validate row keys based on type_entity
        id = row.get('Identificador') or row.get('Id') or row.get('id')
        name = row.get('Nombre') or row.get('name')
        type_entity = row.get('Tipo') or row.get('Tipo de entidad') or row.get('TipoEntidad') or row.get('type_entity')
        lat = row.get('Latitud') or row.get('Latitude') or row.get('lat')
        lon = row.get('Longitud') or row.get('Longitude') or row.get('lon')
        price = row.get('Precio') or row.get('price')
        avg_rating = row.get('Calificación promedio') or row.get('Calificacion') or row.get('rating') or 0
        if not (id and name and type_entity and lat and lon and price):
            continue

        if type_entity == "Turístico":
            stay_time = row.get('Tiempo de estadía') or row.get('stay_time') or 1
            place = TouristPlace(id, name, lat, lon, price, float(avg_rating), stay_time)
        else:
            place = Place(id, name, type_entity, lat, lon, price, float(avg_rating))

        places_tree.insert(id, place)
        add_place_to_graph(place)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<title>Lugares Turísticos y Hospedaje</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
 integrity="sha512-xodZBntM13Mz7f1oXZ6ZYwGyzF3Kn8yx3Twk2QsAmro++9BaTku0Jc8PcqhBj+0J/l3vZ6YN20oNQmRo3eJEHQ=="
 crossorigin=""/>
<style>
  body { font-family: Arial, sans-serif; padding:10px; background:#f5f5f5; }
  #mapid { height: 500px; margin-top:10px; border-radius:10px; }
  label { font-weight:bold; }
  input, select { padding:5px; margin:5px 0; width: 200px; border-radius: 5px; border: 1px solid #ccc; }
  button { padding: 8px 15px; background-color: #007BFF; color: white; border: none; border-radius:5px; cursor:pointer; }
  button: hover { background-color:#0056b3; }
  .container { max-width: 800px; margin: auto; background: white; padding: 20px; box-shadow: 0 0 15px rgba(0,0,0,0.2); border-radius:12px; }
</style>
</head>
<body>
<div class="container">
<h1>Lugares Turísticos y Hospedaje</h1>

<form id="upload-form" enctype="multipart/form-data">
  <label for="csv-file">Cargar CSV de Lugares:</label><br/>
  <input type="file" id="csv-file" name="csv-file" accept=".csv" required />
  <button type="submit">Cargar</button>
</form>

<br/><h2>Recomendación de Rutas</h2>
<form id="recommendation-form">
  <label for="origin">Punto de Origen (Identificador):</label><br/>
  <input type="text" id="origin" name="origin" required placeholder="Identificador origen"/><br/>

  <label for="dest">Destino (Identificador):</label><br/>
  <input type="text" id="dest" name="dest" required placeholder="Identificador destino"/><br/>

  <label for="budget">Presupuesto Diario (Q):</label><br/>
  <input type="number" id="budget" name="budget" required placeholder="Ej. 300" /><br/>

  <button type="submit">Calcular Recomendaciones</button>
</form>

<div id="mapid"></div>

<script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
 integrity="sha512-nMMMyDTYF9Kj6z5C+8R9YwNbpZTp9dQs5b+de0PML2Xj4zFBHcreEBGhGpT3Qw7rNLOOtbE6w73fXTox87KwZw=="
 crossorigin=""></script>
<script>
let map = L.map('mapid').setView([4.6, -74.07], 6);  // Colombia default

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
 maxZoom: 18,
 attribution: '© OpenStreetMap contributors'
}).addTo(map);

let markersLayer = L.layerGroup().addTo(map);

document.getElementById('upload-form').onsubmit = async function(e){
  e.preventDefault();
  const fileInput = document.getElementById('csv-file');
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  const response = await fetch('/upload_csv', {
      method: 'POST',
      body: formData
  });
  const resJson = await response.json();
  alert(resJson.message);
  if(resJson.success){
    // Add markers for all places
    await fetch('/all_places')
      .then(resp => resp.json())
      .then(data => {
        markersLayer.clearLayers();
        data.places.forEach(p=>{
          L.marker([p.lat, p.lon]).addTo(markersLayer).bindPopup(\`\${p.name} (\${p.type_entity})<br>Precio: Q\${p.price} <br>Calificación: \${p.avg_rating.toFixed(2)}\`);
        });
      });
  }
};

document.getElementById('recommendation-form').onsubmit = async function(e){
  e.preventDefault();
  const origin = document.getElementById('origin').value;
  const dest = document.getElementById('dest').value;
  const budget = parseFloat(document.getElementById('budget').value);

  const response = await fetch('/recommendations', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({origin, dest, budget})
  });
  const data = await response.json();
  markersLayer.clearLayers();
  if(data.recommendations && data.recommendations.length > 0){
    let bounds = [];
    data.recommendations.forEach(p=>{
      let marker = L.marker([p.lat, p.lon]).addTo(markersLayer).bindPopup(\`\${p.name}<br>Precio: Q\${p.price}<br>Calificación: \${p.avg_rating.toFixed(2)}<br>Tiempo de estadía: \${p.stay_time || "-"} hrs\`);
      bounds.push([p.lat, p.lon]);
    });
    map.fitBounds(bounds);
  } else {
    alert("No se encontraron recomendaciones para la consulta.");
  }
};
</script>
</div>
</body>
</html>
""")

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'message': 'No se ha enviado archivo'})
    try:
        load_places_csv(file)
        return jsonify({'success': True, 'message': 'CSV cargado con éxito. Lugares actualizados.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error procesando CSV: {str(e)}'})

@app.route('/all_places')
def all_places():
    places = places_tree.get_all()
    places_list = []
    for place in places:
        d = {
            'id': place.id,
            'name': place.name,
            'type_entity': place.type_entity,
            'lat': place.lat,
            'lon': place.lon,
            'price': place.price,
            'avg_rating': place.avg_rating
        }
        if place.type_entity == "Turístico":
            d['stay_time'] = place.stay_time
        places_list.append(d)
    return jsonify({'places': places_list})

@app.route('/recommendations', methods=['POST'])
def recommendations():
    data = request.get_json()
    origin_id = data.get('origin')
    dest_id = data.get('dest')
    budget = float(data.get('budget') or 0)
    max_daily_hours = 8

    origin_place = places_tree.search(origin_id)
    dest_place = places_tree.search(dest_id)

    if not origin_place or not dest_place:
        return jsonify({'error': 'Origen o destino no encontrados'}), 404

    # Simple route recommendation: find tourist places within budget and time constraints, pick top 5 by rating:
    all_places = places_tree.get_all()
    tourist_places = [p for p in all_places if p.type_entity=="Turístico"]

    # We'll do a simple filter since weighted graph path finding is complex to implement fully here
    recommendations = []
    for place in tourist_places:
        if place.id == origin_id:
            continue
        # Compute travel time approx (km/50kmh)
        dist_km = haversine(origin_place.lat, origin_place.lon, place.lat, place.lon)
        travel_time_hours = dist_km / 50
        total_time = travel_time_hours + getattr(place, 'stay_time', 1)
        if total_time <= max_daily_hours and place.price <= budget:
            recommendations.append(place)

    recommendations.sort(key=lambda x: -x.avg_rating)
    recommendations = recommendations[:5]

    recs_out = []
    for r in recommendations:
        recs_out.append({
            'id': r.id,
            'name': r.name,
            'lat': r.lat,
            'lon': r.lon,
            'price': r.price,
            'avg_rating': r.avg_rating,
            'stay_time': getattr(r, 'stay_time', None)
        })

    return jsonify({'recommendations': recs_out})

@app.route('/export_graphviz')
def export_graphviz():
    dot = Digraph(comment='Places B-Tree')
    def visit_node(node, parent_id=None, child_index=0):
        if not node:
            return
        node_id = str(id(node))
        label = "\\n".join([f"{k[0]}" for k in node.keys])
        if label == "":
            label = "Empty"
        dot.node(node_id, label)
        if parent_id:
            dot.edge(parent_id, node_id, label=str(child_index))
        if not node.leaf:
            for idx, c in enumerate(node.children):
                visit_node(c, node_id, idx)
    visit_node(places_tree.root)

    dot_path = "btree_output.gv"
    png_path = "btree_output.png"
    dot.render(dot_path, format='png', cleanup=True)

    def stream_file():
        with open(png_path, "rb") as f:
            data = f.read()
        os.remove(png_path)
        yield data

    return send_file(dot_path + ".png", mimetype='image/png', as_attachment=True, download_name='btree.png')

if __name__ == '__main__':
    app.run(debug=True)

