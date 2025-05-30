class Calificacion:
    def __init__(self, id_lugar, puntaje, comentario=""):
        self.id_lugar = id_lugar
        self.puntaje = float(puntaje)
        self.comentario = comentario or ""

    def __str__(self):
        return f"{self.id_lugar},{self.puntaje},{self.comentario}"

    def to_dict(self):
        return {
            "id_lugar": self.id_lugar,
            "puntaje": self.puntaje,
            "comentario": self.comentario
        }
