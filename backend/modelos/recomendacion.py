from backend.modelos.lugar import LugarNodo
from backend.modelos.utilidadesGrafo import UtilidadesGrafo
# CLASE GRAFO TURISTICO: Representar un grafo de lugares turísticos.

class GrafoTuristico:
    def __init__(self):
        self.nodos = {}  # Diccionario {id: LugarNodo}

    def agregar_lugar(self, lugar):
        self.nodos[lugar.id] = lugar

    def conectar_lugares(self):
        for id_origen, origen in self.nodos.items():
            for id_destino, destino in self.nodos.items():
                if id_origen != id_destino:
                    distancia = UtilidadesGrafo.haversine(
                        origen.latitud, origen.longitud,
                        destino.latitud, destino.longitud
                    )
                    tiempo = UtilidadesGrafo.tiempo_traslado(distancia)
                    origen.agregar_adyacente(destino, tiempo)

    def obtener_nodos(self):
        return list(self.nodos.values())
