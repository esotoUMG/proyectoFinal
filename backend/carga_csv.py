import csv
import io
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 

# Función para cargar lugares desde archivo CSV
def cargar_lugares_csv(archivo, arbol):
    """
    Recibe un archivo CSV y un Árbol B.
    Crea objetos Lugar y los inserta en el Árbol.
    """
    contenido = archivo.read().decode('utf-8')
    lector = csv.DictReader(io.StringIO(contenido))

    for fila in lector:
        if all(k in fila for k in ["id", "nombre", "tipo", "latitud", "longitud", "precio", "calificacion"]):
            lugar = Lugar(
                id=fila['id'],
                nombre=fila['nombre'],
                tipo=fila['tipo'],
                latitud=fila['latitud'],
                longitud=fila['longitud'],
                precio=fila['precio'],
                calificacion=fila['calificacion'],
                tiempo_estadia=fila.get('tiempo_estadia')
            )
            arbol.insertar(lugar)

# Función para cargar calificaciones desde archivo CSV
def cargar_calificaciones_csv(archivo, arbol):
    """
    Recibe un archivo CSV con calificaciones.
    Busca el lugar en el Árbol y le agrega la calificación.
    """
    contenido = archivo.read().decode('utf-8')
    lector = csv.DictReader(io.StringIO(contenido))

    for fila in lector:
        if "id" in fila and "puntaje" in fila:
            id_lugar = fila['id']
            puntaje = fila['puntaje']
            comentario = fila.get('comentario')

            lugar = arbol.buscar(id_lugar)
            if lugar:
                lugar.agregar_calificacion(float(puntaje), comentario)
