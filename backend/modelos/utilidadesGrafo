from graphviz import Digraph
from math import radians, cos, sin , sqrt, atan2

class UtilidadesGrafo:
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 #Radio de la Tierra en km
        dlat = radians(lat2-lat1)
        dlon = radians(lon2-lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    @staticmethod
    def tiempoTraslado(distanciaKM, velocidadKMH=40):
        return distanciaKM / velocidadKMH
    @staticmethod
    def exportarGrafo(grafo):
        dot = Digraph()
        for nodo in grafo.obtener_nodos():
            dot.node(str(nodo.id),nodo.nombre)
        for origen in grafo.obtener_nodos():
            for destino, peso in origen.adyacentes:
                dot.edge(str(origen.id),str(destino.id),label=f"{peso:.2f}")
        dot.render("grafoTuristico", format="png")
