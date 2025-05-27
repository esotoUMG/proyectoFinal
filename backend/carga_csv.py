import csv
import io
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 

# Función para cargar lugares desde archivo CSV
def cargar_lugares_csv(archivo, arbol_b):
    decoded = archivo.read().decode('utf-8-sig').splitlines()
    reader = csv.DictReader(decoded)

    for fila in reader:
        lugar = Lugar(
            id=fila['ï»¿Id'] if 'ï»¿Id' in fila else fila.get('Id'),  # detectar el campo correcto
            departamento=fila['Departamento'],
            municipio=fila['Municipio'],
            nombre=fila['Nombre'],
            tipo=fila['Tipo'],
            direccion=fila['Dirección'],
            latitud=fila['Latitud'],
            longitud=fila['Longitud'],
            calificacion=fila['Calificación en Google'],
            tiempo_estadia=fila.get('tiempo')
        )
        arbol_b.insertar(lugar)


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
