import heapq

# Grafo ponderado utilizando el algoritmo de Dijkstra
class GrafoPonderado:
    def __init__(self):
        self.grafo = {}
    def agregar_vertice(self, vertice):
        if vertice not in self.grafo:
            self.grafo[vertice] = []
    def agregar_arista(self, vertice1, vertice2, peso):
        self.grafo[vertice1].append((vertice2, peso))
        self.grafo[vertice2].append((vertice1, peso)) # Grafo no dirigido
    def dijkstra(self, inicio):
        # Inicialización de distancias y cola de prioridad
        distancias = {vertice: float('infinity') for vertice in self.grafo}
        distancias[inicio] = 0
        cola_prioridad = [(0, inicio)]  # (distancia, vertice)
        while cola_prioridad:
            distancia_actual, vertice_actual = heapq.heappop(cola_prioridad)
            # Si la distancia actual es mayor que la registrada, se ignora
            if distancia_actual > distancias[vertice_actual]:
                continue
            # Recorre los vecinos del vértice actual
            for vecino, peso in self.grafo[vertice_actual]:
                distancia = distancia_actual + peso
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    heapq.heappush(cola_prioridad, (distancia, vecino))
        return distancias
    def graficar_grafo(places_graph):
        dot = Digraph(comment="Grafo de lugares turísticos")

        # Agregar nodos
        current = places_graph.head
        while current:
            label = f"{current.data.name}\n{current.key}"
            dot.node(current.key, label)
            current = current.next

        # Agregar aristas
        current = places_graph.head
        added_edges = set()
        while current:
            edge = current.edges_head
            while edge:
                # Evitar duplicar aristas en grafos no dirigidos
                edge_key = tuple(sorted((current.key, edge.to_node.key)))
                if edge_key not in added_edges:
                    weight_str = f"{edge.weight:.2f} min"
                    dot.edge(current.key, edge.to_node.key, label=weight_str)
                    added_edges.add(edge_key)
                edge = edge.next
            current = current.next

        # Guardar como archivo
        output_path = "static/grafo_ponderado"
        dot.render(output_path, format="png", cleanup=True)
        return f"/{output_path}.png"
