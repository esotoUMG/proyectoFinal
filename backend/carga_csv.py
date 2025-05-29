import csv
import io
import os
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 

# Función para cargar lugares desde archivo CSV
def cargar_lugares_csv(archivo, arbol_lugares, arbol_hospedaje):
    decoded = archivo.read().decode('utf-8-sig').splitlines()
    reader = csv.DictReader(decoded)

    for fila in reader:
        lugar = Lugar(
            id=fila['ï»¿Id'] if 'ï»¿Id' in fila else fila.get('Id'),  
            departamento=fila['Departamento'],
            municipio=fila['Municipio'],
            nombre=fila['Nombre'],
            tipo=fila['Tipo'],
            direccion=fila['Dirección'],
            latitud=fila['Latitud'],
            longitud=fila['Longitud'],
            calificacion=fila['Calificación en Google'],
            precio = fila.get ('Precio'),
            tiempo=fila.get('Tiempo estadia')
        )

        tipo = lugar.tipo.strip().lower()
        if tipo in ['turismo', 'comida', 'entretenimiento']:
            arbol_lugares.insertar(lugar)
        elif tipo in ['hospedaje', 'hotel']:
            arbol_hospedaje.insertar(lugar)
        else:
            print(f"Tipo no reconocido para lugar: {lugar.nombre} -> '{lugar.tipo}'")


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


#Guardar datos en CSV
def guardar_lugar_en_csv(lugar_nuevo, ruta_csv):
    campos = ['Id', 'Departamento', 'Municipio', 'Nombre', 'Tipo', 'Dirección',
              'Latitud', 'Longitud', 'Calificación en Google', 'Tiempo estadia', 'Precio']

    archivo_existe = os.path.isfile(ruta_csv)

    # Verificar si el archivo no termina en salto de línea
    if archivo_existe:
        with open(ruta_csv, 'rb+') as f:
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            if last_char != b'\n':
                f.write(b'\n')

    with open(ruta_csv, mode='a', newline='', encoding='utf-8') as archivo:
        writer = csv.DictWriter(archivo, fieldnames=campos)

        if not archivo_existe:
            writer.writeheader()

        writer.writerow({
            'Id': lugar_nuevo.id,
            'Departamento': lugar_nuevo.departamento,
            'Municipio': lugar_nuevo.municipio,
            'Nombre': lugar_nuevo.nombre,
            'Tipo': lugar_nuevo.tipo,
            'Dirección': lugar_nuevo.direccion,
            'Latitud': lugar_nuevo.latitud,
            'Longitud': lugar_nuevo.longitud,
            'Calificación en Google': lugar_nuevo.calificacion,
            'Tiempo estadia': lugar_nuevo.tiempo if lugar_nuevo.tiempo is not None else '',
            'Precio': lugar_nuevo.precio
        })
