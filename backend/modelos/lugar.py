from .calificacion import Calificacion

# CLASE LUGAR: Representar un lugar turístico o de hospedaje.
class Lugar:
    def __init__(self, id, departamento, municipio, nombre, tipo, direccion, latitud, longitud, calificacion, tiempo, precio):
        self.id = int(id)  # Forzar que id sea entero
        self.departamento = departamento
        self.municipio = municipio
        self.nombre = nombre
        self.tipo = tipo
        self.direccion = direccion
        self.latitud = float(latitud)
        self.longitud = float(longitud)
        self.calificacion = float(calificacion)
        self.tiempo = float(tiempo) if tiempo else None
        self.precio = float(precio)
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
