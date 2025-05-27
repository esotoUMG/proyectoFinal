import os
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
    
    @staticmethod
    def exportarArbol(arbol, nombre_archivo):
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        ruta_completa = os.path.join(escritorio, nombre_archivo)
        
        dot = Digraph(comment='Arbol B')

        def recorrer_nodo(nodo, id_nodo):
            etiquetas = [str(nodo.claves.obtener(i).id) for i in range(nodo.claves.longitud())]
            etiqueta_nodo = " | ".join(etiquetas)
            dot.node(str(id_nodo), label=etiqueta_nodo, shape='record')

            if not nodo.hoja:
                for i in range(nodo.hijos.longitud()):
                    hijo = nodo.hijos.obtener(i)
                    id_hijo = f"{id_nodo}_{i}"
                    recorrer_nodo(hijo, id_hijo)
                    dot.edge(str(id_nodo), id_hijo)

        recorrer_nodo(arbol.raiz, "raiz")

        dot.render(ruta_completa, format="png")
        print(f"Árbol guardado en: {ruta_completa}.png")
