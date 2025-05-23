from .calificacion import Calificacion

# CLASE LUGAR: Representar un lugar turístico o de hospedaje.
class Lugar:
    def __init__(self, id, nombre, tipo, latitud, longitud, precio, calificacion, tiempo_estadia=None):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.latitud = float(latitud)
        self.longitud = float(longitud)
        self.precio = float(precio)
        self.calificacion = float(calificacion)
        self.tiempo_estadia = float(tiempo_estadia) if tiempo_estadia else None
        self.calificaciones = []  # Lista de calificaciones individuales

    def agregar_calificacion(self, puntaje, comentario=None):
        self.calificaciones.append((puntaje, comentario))
        total = sum(p for p, _ in self.calificaciones)
        self.calificacion = total / len(self.calificaciones)

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return f"{self.tipo}: {self.nombre} (Calif. Prom: {self.calificacion:.1f})"
