import csv, os
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 
from backend.modelos.recomendaciones import Recomendaciones
from backend.arbolB import CalificacionNodo, BTree


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
    reader = csv.DictReader(archivo)

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
              'Latitud', 'Longitud', 'Calificación en Google', 'Precio', 'Tiempo estadia']

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

#FUNCIONES PARA LAS CALIFICACIONES
def guardar_calificacion_csv(calificacion, archivo="./data/ratings.csv"):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)

    with open(archivo, "a", encoding="utf-8") as f:
        f.write(f"{calificacion.id},{calificacion.id_lugar},{calificacion.puntaje},{calificacion.comentario}\n")


def insertar_calificacion_en_arbol(arbol_calificaciones, calificacion):
    nodo = arbol_calificaciones.buscar(calificacion.id_lugar)
    if nodo:
        # Nodo existe, agregamos calificación
        nodo.agregar(calificacion)
    else:
        # Nodo no existe, creamos uno nuevo y agregamos
        nuevo_nodo = CalificacionNodo(calificacion.id_lugar)
        nuevo_nodo.agregar(calificacion)
        arbol_calificaciones.insertar(nuevo_nodo)


ultimo_id_calificacion = 0 

def cargar_calificaciones_csv(archivo="calificaciones.csv", arbol_calificaciones=None, arbol_lugares=None):
    global ultimo_id_calificacion
    ultimo_id_calificacion = 0  # Reiniciar ID global solo si se usan IDs automáticos

    if arbol_calificaciones is None or arbol_lugares is None:
        raise ValueError("Se requieren ambos árboles: calificaciones y lugares")

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # saltar encabezado
            for fila in reader:
                if len(fila) >= 3:  # Necesita al menos ID, ID_lugar, puntaje
                    try:
                        id_calificacion = int(fila[0])
                        id_lugar = int(fila[1])
                        puntaje = float(fila[2])
                        comentario = ",".join(fila[3:]) if len(fila) > 3 else ""
                    except ValueError:
                        continue

                    calif = Calificacion(id_calificacion, id_lugar, puntaje, comentario)
                    insertar_calificacion_en_arbol(arbol_calificaciones, calif)

                    # Actualizar promedio en el árbol de lugares
                    lugar = arbol_lugares.buscar(id_lugar)
                    if lugar:
                        cantidad_actual = getattr(lugar, 'cantidad_calificaciones', 0)
                        promedio_actual = getattr(lugar, 'calificacion', 0.0)
                        nuevo_promedio = (promedio_actual * cantidad_actual + puntaje) / (cantidad_actual + 1)
                        lugar.calificacion = nuevo_promedio
                        lugar.cantidad_calificaciones = cantidad_actual + 1

    except FileNotFoundError:
        print("Archivo de calificaciones no encontrado.")

def cargar_calificaciones_desde_csv(id_lugar, archivo="calificaciones.csv"):
    calificaciones = []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # saltar encabezado
            for fila in reader:
                if len(fila) >= 3:
                    try:
                        id_calif = int(fila[0])
                        id_lug = int(fila[1])
                        puntaje = float(fila[2])
                        comentario = ",".join(fila[3:]) if len(fila) > 3 else ""
                        if id_lug == id_lugar:
                            calificaciones.append(Calificacion(id_calif, id_lug, puntaje, comentario))
                    except:
                        continue
    except FileNotFoundError:
        pass
    return calificaciones


