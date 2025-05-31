import csv, signal, sys, os
from backend.modelos.lugar import Lugar
from backend.modelos.calificacion import Calificacion 
from backend.modelos.recomendaciones import Recomendaciones


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
        f.write(f"{calificacion.id_lugar},{calificacion.puntaje},{calificacion.comentario}\n")

def cargar_calificaciones_csv(archivo="calificaciones.csv", arbol_calificaciones=None, arbol_lugares=None):
    if arbol_calificaciones is None or arbol_lugares is None:
        raise ValueError("Se requieren ambos árboles: calificaciones y lugares")

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Saltar encabezado
            for fila in reader:
                if len(fila) >= 2:
                    try:
                        id_lugar = int(fila[0])
                    except ValueError:
                        continue  # Ignorar fila con id no válido

                    try:
                        puntaje = float(fila[1])
                    except ValueError:
                        puntaje = 0.0

                    comentario = ",".join(fila[2:]) if len(fila) > 2 else ""
                    calif = Calificacion(id_lugar, puntaje, comentario)

                    # Insertar en árbol de calificaciones
                    arbol_calificaciones.insertar(id_lugar, calif)

                    # Actualizar promedio en árbol de lugares
                    lugar = arbol_lugares.buscar(id_lugar)  # o tu función para obtener lugar por ID
                    if lugar:
                        cantidad_actual = getattr(lugar, 'cantidad_calificaciones', 0)
                        promedio_actual = getattr(lugar, 'calificacion', 0.0)

                        nuevo_promedio = (promedio_actual * cantidad_actual + puntaje) / (cantidad_actual + 1)
                        lugar.calificacion = nuevo_promedio
                        lugar.cantidad_calificaciones = cantidad_actual + 1

                        # Si tienes función para guardar lugar, la llamas
                        # guardar_lugar(lugar) # Opcional si persistes los lugares
    except FileNotFoundError:
        pass

def guardar_recomendaciones_csv(recomendaciones, archivo="./data/recomendaciones.csv"):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)

    with open(archivo, "b", encoding="utf-8") as f:
        f.write(f"{recomendacion.id},{recomendacion.departamento},{recomendacion.municipio},{recomendacion.nombre},{recomendacion.tipo},{recomendacion.direccion},{recomendacion.latitud},{recomendacion.longitud},{recomendacion.calificacion},{recomendacion.tiempo},{recomendacion.precio},{recomendacion.calificaciones},\n")

# --- Exportar datos.csv desde árbol B ---


def exportar_datos_csv_desde_arbol(arbol_lugares):
    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    ruta = os.path.join(escritorio, 'datos.csv')

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['Nombre', 'Descripción', 'Categoría', 'Precio', 'Tiempo Estadia', 'Latitud', 'Longitud'])

        lugares = []

        def recorrer_nodo(nodo):
            if nodo is None:
                return
            # Nodo puede tener claves (lugares) y subnodos (hijos)
            for i in range(len(nodo.claves)):
                # Recorrer hijo izquierdo
                if nodo.hijos and len(nodo.hijos) > i:
                    recorrer_nodo(nodo.hijos[i])
                # Agregar clave actual
                lugares.append(nodo.claves[i])
            # Recorrer último hijo derecho
            if nodo.hijos and len(nodo.hijos) > len(nodo.claves):
                recorrer_nodo(nodo.hijos[len(nodo.claves)])

        recorrer_nodo(arbol_lugares.raiz)

        for lugar in lugares:
            writer.writerow([
                getattr(lugar, 'nombre', ''),
                getattr(lugar, 'descripcion', ''),
                getattr(lugar, 'categoria', ''),
                getattr(lugar, 'precio', 0),
                getattr(lugar, 'tiempo_estadia', 0),
                getattr(lugar, 'latitud', 0),
                getattr(lugar, 'longitud', 0)
            ])

    print(f"datos.csv actualizado guardado en: {ruta}")

# --- Exportar ratings.csv desde árbol de calificaciones ---

def exportar_ratings_csv_desde_arbol(arbol_calificaciones):
    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    ruta = os.path.join(escritorio, 'ratings.csv')

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['IdLugar', 'Puntaje', 'Comentario'])

        calificaciones = []

        def recorrer_nodo_cal(nodo):
            if nodo is None:
                return
            for i in range(len(nodo.claves)):
                if nodo.hijos and len(nodo.hijos) > i:
                    recorrer_nodo_cal(nodo.hijos[i])
                calificaciones.append(nodo.claves[i])
            if nodo.hijos and len(nodo.hijos) > len(nodo.claves):
                recorrer_nodo_cal(nodo.hijos[len(nodo.claves)])

        recorrer_nodo_cal(arbol_calificaciones.raiz)

        # calificaciones aquí son nodos CalificacionNodo, con lista enlazada dentro
        for calif_nodo in calificaciones:
            actual = calif_nodo.calificaciones.primero
            while actual:
                c = actual.dato
                writer.writerow([c.id_lugar, c.puntaje, c.comentario])
                actual = actual.siguiente

    print(f"ratings.csv actualizado guardado en: {ruta}")

# --- Exportar recomendaciones.csv (tuya) ---

def exportar_recomendaciones_csv(nodos, aristas):
    escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
    ruta = os.path.join(escritorio, 'recomendaciones.csv')

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['Nodo Principal', nodos[0] if nodos else ''])
        writer.writerow([])
        writer.writerow(['Recomendación', 'Peso'])

        for arista in aristas:
            if arista['origen'] == (nodos[0] if nodos else None):
                writer.writerow([arista['destino'], arista['peso']])

    print(f"recomendaciones.csv guardado en: {ruta}")

# --- Handler de salida ---

def handler_exit(signum, frame):
    print("Servidor cerrándose. Exportando datos...")

    try:
        exportar_recomendaciones_csv(nodos, aristas)
        exportar_datos_csv_desde_arbol(lugares_arbol)
        exportar_ratings_csv_desde_arbol(arbol_calificaciones)
        exportar_ratings_csv_desde_arbol(hospedajes_arbol)
        print("Datos exportados correctamente.")
    except Exception as e:
        print(f"Error al exportar: {e}")

    sys.exit(0)

# Registrar las señales de salida
signal.signal(signal.SIGINT, handler_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handler_exit)  # kill PID
