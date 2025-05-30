from graphviz import Digraph
import os
import math

def generar_grafo_ponderado(nodos, aristas, id_grafo):
    grafo = Digraph(comment='Grafo ponderado', engine='neato')

    if not nodos:
        raise ValueError("Lista de nodos vacía")

    nodo_principal = nodos[0]
    recomendaciones = nodos[1:]

    # Nodo principal en el centro
    centro_x, centro_y = 50, 50
    grafo.node(nodo_principal, shape='doublecircle', style='filled', fillcolor='lightblue', pos=f'{centro_x},{centro_y}!')

    # Obtener pesos entre nodo_principal y recomendaciones
    pesos = []
    for nodo in recomendaciones:
        peso_raw = next((a['peso'] for a in aristas if a['origen'] == nodo_principal and a['destino'] == nodo), 1)
        try:
            peso = float(str(peso_raw).split()[0])
        except:
            peso = 1
        pesos.append(peso)

    peso_min = min(pesos) if pesos else 1
    peso_max = max(pesos) if pesos else 1

    # Distancia radial: menor peso = más cerca del centro
    def escalar_distancia(peso):
        min_dist, max_dist = 5, 15
        if peso_max == peso_min:
            return (min_dist + max_dist) / 2
        return min_dist + ((peso - peso_min) * (max_dist - min_dist) / (peso_max - peso_min))


    # Nodo con menor peso
    nodo_destacado = recomendaciones[pesos.index(peso_min)] if recomendaciones else None

    # Posicionar nodos en círculo
    n = len(recomendaciones)
    for i, nodo in enumerate(recomendaciones):
        peso = pesos[i]
        distancia = escalar_distancia(peso)
        angulo = 2 * math.pi * i / n

        x = centro_x + distancia * math.cos(angulo)
        y = centro_y + distancia * math.sin(angulo)

        color = 'lightgreen' if nodo == nodo_destacado else 'white'
        grafo.node(nodo, shape='circle', style='filled', fillcolor=color, pos=f'{x:.2f},{y:.2f}!')

    # Aristas
    pesos_aristas = []
    for a in aristas:
        try:
            val = float(str(a.get('peso', '1')).split()[0])
        except:
            val = 1
        pesos_aristas.append(val)

    peso_min_arista = min(pesos_aristas) if pesos_aristas else 1
    peso_max_arista = max(pesos_aristas) if pesos_aristas else 1

    def escalar_penwidth(peso):
        if peso_max_arista == peso_min_arista:
            return 3
        return 1 + 4 * (peso - peso_min_arista) / (peso_max_arista - peso_min_arista)

    for arista in aristas:
        origen = arista['origen']
        destino = arista['destino']
        peso_raw = arista.get('peso', 1)
        try:
            peso = float(str(peso_raw).split()[0])
        except:
            peso = 1
        penwidth = escalar_penwidth(peso)
        grafo.edge(origen, destino, label=str(peso_raw), penwidth=str(penwidth))

    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    nombre_archivo = f'grafoponderado{id_grafo}'
    ruta_archivo = os.path.join(escritorio, nombre_archivo)

    grafo.render(ruta_archivo, format='png', cleanup=True)

    return ruta_archivo + '.png'
