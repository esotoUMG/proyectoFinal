import math

# CLASE NODO: Representa un nodo dentro del Árbol B.
class Nodo:
    def __init__(self, grado, hoja=False):
        self.grado = grado       # Grado del árbol B (número máximo de hijos por nodo)
        self.hoja = hoja         # Determina si el nodo es una hoja (si tiene hijos o no)
        self.claves = []         # Lista de claves almacenadas en el nodo
        self.hijos = []          # Lista de hijos (solo presente si el nodo no es hoja)

# CLASE ARBOL B: Representa un Árbol B, una estructura de datos balanceada.
class Btree:
    def __init__(self, grado):
        self.grado = grado                               # Grado del árbol B
        self.raiz = Nodo(grado, True)                    # Raíz del árbol, inicialmente una hoja
        self.max_claves = grado - 1                      # Número máximo de claves en un nodo
        self.min_claves = math.ceil((grado + 1) / 2) - 1  # Número mínimo de claves en un nodo (para balanceo)

    # Método para dividir un hijo cuando está lleno y no cabe una nueva clave.
    def dividirHijo(self, padre, i):
        grado = self.grado
        y = padre.hijos[i]          # Nodo hijo que será dividido
        z = Nodo(grado, y.hoja)     # Nuevo nodo que tomará parte de las claves de y
        medio = len(y.claves) // 2  # Indice de la clave media

        # Insertar la clave media en el padre
        padre.claves.insert(i, y.claves[medio])
        padre.hijos.insert(i + 1, z)  # Añadir el nuevo hijo

        # Repartir las claves entre el nodo original y el nuevo
        z.claves = y.claves[medio + 1:]
        y.claves = y.claves[:medio]

        # Si el nodo y no es hoja, también se deben dividir los hijos
        if not y.hoja:
            z.hijos = y.hijos[medio + 1:]
            y.hijos = y.hijos[:medio + 1]

    # Método recursivo que realiza la inserción de una clave en el nodo adecuado después de dividir.
    def _insertar_post_division(self, nodo, k):
        i = len(nodo.claves) - 1
        if nodo.hoja:  # Si el nodo es una hoja, se inserta la clave directamente
            nodo.claves.append(None)
            while i >= 0 and k < nodo.claves[i]:
                nodo.claves[i + 1] = nodo.claves[i]  # Desplazar las claves mayores para hacer espacio
                i -= 1
            nodo.claves[i + 1] = k  # Insertar la nueva clave
        else:
            # Si el nodo no es hoja, buscar el hijo adecuado para la clave
            while i >= 0 and k < nodo.claves[i]:
                i -= 1
            i += 1
            self._insertar_post_division(nodo.hijos[i], k)  # Llamar recursivamente para insertar en el hijo

            # Si el hijo ha excedido el número máximo de claves, se debe dividir
            if len(nodo.hijos[i].claves) > self.max_claves:
                self.dividirHijo(nodo, i)  # Dividir el hijo y ajustar el árbol

    # Método para insertar una clave en el árbol B.
    def insertar(self, k):
        raiz = self.raiz
        self._insertar_post_division(raiz, k)  # Llamada para insertar la clave en la raíz
        if len(self.raiz.claves) > self.max_claves:  # Si la raíz está llena, dividirla
            s = Nodo(self.grado, False)  # Crear una nueva raíz
            s.hijos.append(self.raiz)    # Hacer que la antigua raíz sea un hijo de la nueva raíz
            self.dividirHijo(s, 0)       # Dividir la nueva raíz
            self.raiz = s                # La nueva raíz ahora es la raíz del árbol

    # MÉTODO PARA BUSCAR NODOS DENTRO DEL ÁRBOL
    def buscar(self, k):
        return self._buscar_en_nodo(self.raiz, k)  # Llamada para buscar la clave en el árbol

    # Método recursivo para buscar la clave en un nodo.
    def _buscar_en_nodo(self, nodo, k):
        i = 0
        while i < len(nodo.claves) and k > nodo.claves[i]:
            i += 1
        if i < len(nodo.claves) and k == nodo.claves[i]:  # Si la clave se encuentra en el nodo
            return True
        elif nodo.hoja:  # Si es hoja, la clave no se encuentra
            return False
        else:
            return self._buscar_en_nodo(nodo.hijos[i], k)  # Buscar en el hijo correspondiente

    # MÉTODO DE ELIMINACIÓN DE NODOS
    def eliminar(self, k):
        return self._eliminar_de_nodo(self.raiz, k)  # Llamada para eliminar la clave

    # Método recursivo para eliminar la clave de un nodo.
    def _eliminar_de_nodo(self, nodo, k):
        if k in nodo.claves:  # Si la clave se encuentra en el nodo, eliminarla
            nodo.claves.remove(k)
            return True
        for hijo in nodo.hijos:  # Buscar en los hijos si la clave no está en el nodo
            if self._eliminar_de_nodo(hijo, k):
                return True  # Si la clave fue eliminada en algún hijo
        return False  # Si la clave no se encontró en el árbol
