import csv, io, signal, sys, os
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 

import csv
import io
import os
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 

def safe_float(valor, default=0.0):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return default

def safe_int(valor, default=0):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return default

# Función para cargar lugares desde archivo CSV
def cargar_lugares_csv(archivo, arbol_lugares, arbol_hospedaje):
    decoded = archivo.read().decode('utf-8-sig').splitlines()
    reader = csv.DictReader(decoded)

    for fila in reader:
        id_lugar = fila['ï»¿Id'] if 'ï»¿Id' in fila else fila.get('Id')
        # Si esperas que id sea entero, conviértelo seguro
        id_lugar = safe_int(id_lugar)

        latitud = safe_float(fila['Latitud'])
        longitud = safe_float(fila['Longitud'])
        calificacion = safe_float(fila['Calificación en Google'])
        precio = safe_float(fila.get('Precio', '0'))
        tiempo = safe_float(fila.get('Tiempo estadia', '0'))

        lugar = Lugar(
            id=id_lugar,
            departamento=fila['Departamento'],
            municipio=fila['Municipio'],
            nombre=fila['Nombre'],
            tipo=fila['Tipo'],
            direccion=fila['Dirección'],
            latitud=latitud,
            longitud=longitud,
            calificacion=calificacion,
            precio=precio,
            tiempo=tiempo
        )

        tipo = lugar.tipo.strip().lower()
        if tipo in ['turismo', 'comida', 'entretenimiento']:
            arbol_lugares.insertar(lugar)
        elif tipo in ['hospedaje', 'hotel']:
            arbol_hospedaje.insertar(lugar)
        else:
            print(f"Tipo no reconocido para lugar: {lugar.nombre} -> '{lugar.tipo}'")


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


# Función para cargar calificaciones desde archivo CSV
def cargar_calificaciones_csv(archivo, arbol):
    """
    Recibe un archivo CSV con calificaciones.
    Busca el lugar en el Árbol y le agrega la calificación.
    """
    contenido = archivo.read().decode('utf-8')
    lector = csv.DictReader(io.StringIO(contenido))

    for fila in lector:
        if "Id" in fila and "Puntaje" in fila:
            try:
                id_lugar = int(fila['Id'])
                puntaje = float(fila['Puntaje'])
                comentario = fila.get('Comentario', '')

                lugar = arbol.buscar(id_lugar)
                if lugar:
                    lugar.agregar_calificacion(puntaje, comentario)
            except ValueError:
                # Ignorar filas con datos inválidos
                continue

def guardar_calificacion_en_csv(ruta_csv, id_lugar, puntaje, comentario):
    archivo_existe = os.path.isfile(ruta_csv)

    with open(ruta_csv, mode='a', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)

        if not archivo_existe:
            escritor.writerow(['Id', 'Puntaje', 'Comentario'])

        escritor.writerow([id_lugar, puntaje, comentario])


        
def actualizar_calificacion_promedio_csv(ruta_csv_lugares, arbol):
    """
    Lee el CSV original de lugares, actualiza la columna de calificación
    con el promedio almacenado en los objetos Lugar del árbol, y sobrescribe el archivo.
    """
    filas_actualizadas = []

    with open(s_lugares, mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        campos = lector.fieldnames

        for fila in lector:
            id_lugar = int(fila['Id'])
            lugar = arbol.buscar(id_lugar)
            if lugar:
                # Actualizar solo la calificación promedio en la fila
                fila['Calificación en Google'] = f"{lugar.calificacion:.2f}"
            filas_actualizadas.append(fila)

    # Sobrescribir archivo con las filas actualizadas
    with open(ruta_csv_lugares, mode='w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas_actualizadas)

#Funcion para exportar los documentos en formato CSV
def exportar_recomendaciones_csv(nodos, aristas):
    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    ruta = os.path.join(escritorio, 'recomendaciones.csv')

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['Nodo Principal', nodos[0]])
        writer.writerow([])
        writer.writerow(['Recomendación', 'Peso'])

        for arista in aristas:
            if arista['origen'] == nodos[0]:
                writer.writerow([arista['destino'], arista['peso']])
    
    print(f"recomendaciones.csv guardado en: {ruta}")

def exportar_datos_csv(lista_lugares):
    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    ruta = os.path.join(escritorio, 'datos.csv')

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['Nombre', 'Descripción', 'Categoría', 'Precio', 'Tiempo Estadia', 'Latitud', 'Longitud'])  # Ajusta según campos reales

        actual = lista_lugares.primero  # Asumiendo lista enlazada personalizada
        while actual:
            lugar = actual.valor
            writer.writerow([
                lugar.nombre,
                lugar.descripcion,
                lugar.categoria,
                lugar.precio,
                lugar.tiempo_estadia,
                lugar.latitud,
                lugar.longitud
            ])
            actual = actual.siguiente

    print(f"datos.csv actualizado guardado en: {ruta}")

nodos = []     
aristas = []   
lugares_arbol = None  

def handler_exit(signum, frame):
    print("Servidor cerrándose. Exportando datos...")

    try:
        exportar_recomendaciones_csv(nodos, aristas)
        exportar_datos_csv(lugares_arbol)  # Este debe ser tu árbol u otra estructura de lugares
        print("Datos exportados correctamente.")
    except Exception as e:
        print(f"Error al exportar: {e}")

    sys.exit(0)

# Registrar las señales de salida
signal.signal(signal.SIGINT, handler_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handler_exit)  # kill PID