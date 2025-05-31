class Recomendaciones:
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
        self.calificaciones = []

    def __str__(self):
        return f"{self.id},{self.departamento},{self.municipio},{self.nombre},{self.tipo},{self.direccion},{self.latitud},{self.longitud},{self.calificacion},{self.tiempo},{self.precio},{self.calificaciones}"

    def to_dict(self):
        return {
            "id":self.id ,
            "departamento":self.departamento,
            "municipio":self.municipio,
            "nombre":self.nombre,
            "tipo":self.tipo,
            "direccion":self.direccion,
            "latitud":self.latitud,
            "longitud":self.longitud,
            "calificacion":self.calificacion,
            "tiempo":self.tiempo,
            "precio":self.precio,
            "calificaciones":self.calificaciones,
        }
