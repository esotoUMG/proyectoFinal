class Calificacion:
    def __init__(self, id, id_lugar, puntaje, comentario):
        self.id = id            # ID único de esta calificación
        self.id_lugar = id_lugar  # Lugar asociado
        self.puntaje = puntaje
        self.comentario = comentario

    def __str__(self):
        return f"{self.id},{self.id_lugar},{self.puntaje},{self.comentario}"

    def to_dict(self):
        return {
            "id": self.id,
            "id_lugar": self.id_lugar,
            "puntaje": self.puntaje,
            "comentario": self.comentario
        }



