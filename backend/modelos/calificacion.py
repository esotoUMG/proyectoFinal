
#CLASE CALIFICACION: Representar una calificación individual de un lugar.
class Calificacion:
    def __init__(self, id_lugar, puntaje, comentario=None):
        self.id_lugar = id_lugar
        self.puntaje = float(puntaje)
        self.comentario = comentario

    def __str__(self):
        return f"Puntaje: {self.puntaje}, Comentario: {self.comentario if self.comentario else 'Sin comentario'}"
