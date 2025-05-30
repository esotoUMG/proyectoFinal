import heapq
import graphviz
from graphviz import Digraph
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
    
    def graficar_grafo(self):
        dot = Digraph(comment="Grafo de lugares turísticos")

        # Agregar nodos
        for vertice in self.grafo:
            dot.node(vertice, vertice)  # Puedes cambiar el label si tienes nombres

        # Agregar aristas (evitando duplicados)
        aristas_agregadas = set()
        for vertice, vecinos in self.grafo.items():
            for vecino, peso in vecinos:
                # Evitar duplicar aristas en grafo no dirigido
                arista = tuple(sorted((vertice, vecino)))
                if arista not in aristas_agregadas:
                    dot.edge(vertice, vecino, label=f"{peso:.2f} min")
                    aristas_agregadas.add(arista)

        # Guardar como archivo PNG
        output_path = "static/grafo_ponderado"
        dot.render(output_path, format="png", cleanup=True)
        return f"/{output_path}.png"
    
def calcular_peso_total(lugar1, lugar2, tiempo_traslado):
    # Peso calificación: menor si la calificación es más alta
    peso_calificacion = 5 - ((lugar1.calificacion + lugar2.calificacion) / 2)

    # Peso total (ajusta los coeficientes según prioridad)
    return (
        (lugar1.precio + lugar2.precio) * 1.0 +
        (lugar1.tiempo_estadia + lugar2.tiempo_estadia) * 1.5 +
        tiempo_traslado * 2.0 +
        peso_calificacion * 3.0
    )
