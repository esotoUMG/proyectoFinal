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
