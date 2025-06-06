import math



# Clase NodoLista: Nodo individual de una lista enlazada
class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

# Clase Lista: Lista enlazada personalizada (sin listas nativas)
class Lista:
    def __init__(self):
        self.primero = None
        self._longitud = 0

    def insertar(self, dato, pos=None):
        nuevo = NodoLista(dato)
        if self.primero is None or pos == 0:
            nuevo.siguiente = self.primero
            self.primero = nuevo
        else:
            anterior = None
            actual = self.primero
            indice = 0
            while actual and (pos is None or indice < pos):
                anterior = actual
                actual = actual.siguiente
                indice += 1
            nuevo.siguiente = actual
            if anterior:
                anterior.siguiente = nuevo
        self._longitud += 1

    def eliminar(self, pos):
        if self.primero is None:
            return
        actual = self.primero
        if pos == 0:
            self.primero = actual.siguiente
        else:
            anterior = None
            indice = 0
            while actual and indice < pos:
                anterior = actual
                actual = actual.siguiente
                indice += 1
            if anterior and actual:
                anterior.siguiente = actual.siguiente
        self._longitud -= 1

    def obtener(self, pos):
        actual = self.primero
        indice = 0
        while actual:
            if indice == pos:
                return actual.dato
            actual = actual.siguiente
            indice += 1
        return None

    def reemplazar(self, pos, nuevo_valor):
        actual = self.primero
        indice = 0
        while actual:
            if indice == pos:
                actual.dato = nuevo_valor
                return
            actual = actual.siguiente
            indice += 1

    def longitud(self):
        return self._longitud

    def insertar_ordenado(self, dato):
        actual = self.primero
        indice = 0
        while actual:
            if dato < actual.dato:
                break
            actual = actual.siguiente
            indice += 1
        self.insertar(dato, indice)

    def recorrer(self):
        actual = self.primero
        resultado = []
        while actual:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado


# Clase Nodo: Nodo del Árbol B
class Nodo:
    def __init__(self, grado, hoja=False):
        self.grado = grado
        self.hoja = hoja
        self.claves = Lista()
        self.hijos = Lista()


# Clase BTree: Árbol B usando Lista personalizada
class BTree:
    
    def __init__(self, grado):
        self.grado = grado
        self.raiz = Nodo(grado, True)
        self.max_claves = grado - 1
        self.min_claves = math.ceil((grado + 1) / 2) - 1

    def insertar(self, lugar):
        raiz = self.raiz
        if raiz.claves.longitud() == self.max_claves:
            nueva_raiz = Nodo(self.grado, False)
            nueva_raiz.hijos.insertar(raiz)
            self._dividir_hijo(nueva_raiz, 0)
            self._insertar_no_lleno(nueva_raiz, lugar)
            self.raiz = nueva_raiz
        else:
            self._insertar_no_lleno(raiz, lugar)

    def _insertar_no_lleno(self, nodo, lugar):
        i = nodo.claves.longitud() - 1
        if nodo.hoja:
            nodo.claves.insertar_ordenado(lugar)
        else:
            while i >= 0 and lugar < nodo.claves.obtener(i):
                i -= 1
            i += 1
            hijo = nodo.hijos.obtener(i)
            if hijo.claves.longitud() == self.max_claves:
                self._dividir_hijo(nodo, i)
                if lugar > nodo.claves.obtener(i):
                    i += 1
            self._insertar_no_lleno(nodo.hijos.obtener(i), lugar)

    def _dividir_hijo(self, padre, i):
        hijo = padre.hijos.obtener(i)
        nuevo = Nodo(self.grado, hijo.hoja)
        medio = self.grado // 2

        clave_media = hijo.claves.obtener(medio)
        padre.claves.insertar(clave_media, i)
        padre.hijos.insertar(nuevo, i + 1)

        for j in range(medio + 1, hijo.claves.longitud()):
            nuevo.claves.insertar(hijo.claves.obtener(j))
        for j in range(hijo.claves.longitud() - 1, medio - 1, -1):
            hijo.claves.eliminar(j)

        if not hijo.hoja:
            for j in range(medio + 1, hijo.hijos.longitud()):
                nuevo.hijos.insertar(hijo.hijos.obtener(j))
            for j in range(hijo.hijos.longitud() - 1, medio, -1):
                hijo.hijos.eliminar(j)

    def buscar(self, id_lugar):
        return self._buscar_en_nodo(self.raiz, id_lugar)

    def _buscar_en_nodo(self, nodo, id_lugar):
        i = 0
        while i < nodo.claves.longitud() and id_lugar > nodo.claves.obtener(i).id:
            i += 1
        if i < nodo.claves.longitud() and nodo.claves.obtener(i).id == id_lugar:
            return nodo.claves.obtener(i)
        elif nodo.hoja:
            return None
        else:
            return self._buscar_en_nodo(nodo.hijos.obtener(i), id_lugar)

    def eliminar(self, id_lugar):
        return self._eliminar_de_nodo(self.raiz, id_lugar)

    def _eliminar_de_nodo(self, nodo, id_lugar):
        for i in range(nodo.claves.longitud()):
            if nodo.claves.obtener(i).id == id_lugar:
                nodo.claves.eliminar(i)
                return True
        for i in range(nodo.hijos.longitud()):
            if self._eliminar_de_nodo(nodo.hijos.obtener(i), id_lugar):
                return True
        return False
        
    def obtener_lugares(self):
        lugares = []
        self._recorrer(self.raiz, lugares)
        return lugares
    
    def obtener_calificaciones(self):
        calificaciones = []
        self._recorrer(self.raiz, calificaciones)
        return calificaciones

    def _recorrer(self, nodo, lista):
        for i in range(nodo.claves.longitud()):
            lista.append(nodo.claves.obtener(i))
        if not nodo.hoja:
            for i in range(nodo.hijos.longitud()):
                self._recorrer(nodo.hijos.obtener(i), lista)

    def buscar_por_nombre(self, nombre):
        for lugar in self.obtener_lugares():
            if lugar.nombre.strip().lower() == nombre.strip().lower():
                return lugar
        return None
    
    def recorrer(self):
        resultados = []
        self._recorrer(self.raiz, resultados)
        return resultados
    


class CalificacionNodo:
    def __init__(self, id_lugar):
        self.id_lugar = id_lugar  # Identificador del lugar, clave del nodo
        self.calificaciones = Lista()  # Lista de objetos Calificacion

    @property
    def id(self):
        # Esto es lo que usa el árbol para indexar (no cambiar)
        return self.id_lugar

    def agregar(self, calificacion):
        self.calificaciones.insertar(calificacion)

    def promedio(self):
        total = 0
        n = self.calificaciones.longitud()
        if n == 0:
            return 0
        actual = self.calificaciones.primero
        while actual:
            total += actual.dato.puntaje
            actual = actual.siguiente
        return total / n

    def to_dict(self):
        return {
            "id": self.id_lugar,
            "id_lugar": self.id_lugar,
            "promedio": self.promedio(),
            "calificaciones": [c.to_dict() for c in self.calificaciones.recorrer()]
        }

    def buscar_calificacion(self, id_calificacion):
        actual = self.calificaciones.primero
        while actual:
            if actual.dato.id_calificacion == id_calificacion:
                return actual.dato
            actual = actual.siguiente
        return None

    def eliminar_calificacion(self, id_calificacion):
        actual = self.calificaciones.primero
        prev = None
        indice = 0
        while actual:
            if actual.dato.id_calificacion == id_calificacion:
                # eliminar en lista enlazada
                if prev is None:
                    self.calificaciones.primero = actual.siguiente
                else:
                    prev.siguiente = actual.siguiente
                self.calificaciones._longitud -= 1
                return True
            prev = actual
            actual = actual.siguiente
            indice += 1
        return False

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id




