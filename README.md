# 🌍 TravelMap

**TravelMap** es una aplicación web desarrollada como proyecto final del curso **Programación III** en la Universidad Mariano Gálvez, sede Naranjo. El sistema permite a los usuarios **registrar, consultar y calificar lugares turísticos y hospedajes**, generar **rutas recomendadas personalizadas** según sus preferencias, visualizar recorridos en un **mapa interactivo**, y todo esto respaldado con estructuras de datos propias como **Árbol B** y **grafos ponderados**.

---

## 🎯 Objetivo del Proyecto

Desarrollar un sistema de planificación turística inteligente que ayude a los usuarios a:
- Tomar decisiones informadas sobre qué lugares visitar
- Obtener recomendaciones optimizadas según su presupuesto, tiempo disponible y calificaciones
- Visualizar rutas completas en mapa
- Calificar sus experiencias

---

## 🚀 Funcionalidades principales

- 📁 **Carga masiva** de lugares turísticos y hospedajes desde archivos CSV
- 🧭 **Generación de rutas recomendadas** usando grafos ponderados y árboles de decisión
- 🗺️ **Visualización de rutas** en mapa interactivo con Google Maps
- ⭐ **Sistema de calificaciones** y comentarios por parte de los usuarios
- 📊 **Estructuras internas eficientes** como Árbol B para almacenamiento y búsqueda
- 🌐 **Interfaz intuitiva** construida con HTML, CSS y JavaScript

---

## 🛠️ Tecnologías y Herramientas Utilizadas

| Herramienta           | Descripción                                                        |
|------------------------|--------------------------------------------------------------------|
| **Python 3.11+**       | Lenguaje principal para el backend                                |
| **Flask**              | Microframework web para manejar rutas, formularios y API REST     |
| **HTML5 / CSS3**       | Estructura y diseño de la interfaz de usuario                     |
| **JavaScript**         | Interactividad del frontend y validaciones                        |
| **Google Maps API**    | Visualización de rutas sobre mapas reales                         |
| **Graphviz**           | Visualización gráfica de árboles y grafos                         |
| **Visual Studio Code** | Entorno de desarrollo                                              |
| **CSV module (Python)**| Manejo de carga masiva desde archivos CSV                         |

---

## ✅ Requisitos Previos

- Python 3.11 o superior  
- pip instalado  
- Conexión a internet (para Google Maps)  
- Archivos CSV válidos con los lugares y calificaciones  

---

## 🔧 Instalación y Configuración

1. **Clona el repositorio:**

```bash
git clone https://github.com/usuario/travelmap.git
cd travelmap
```

2. **Instala las dependencias:**

```bash
pip install flask graphviz
```
3. **Ejecuta la aplicacion:**

```bash
python app.py

```
3. **Accede al navegador:**

```bash
http://localhost:5000

```

## 📦 Estructura del Proyecto

```bash
TravelMap/
├── backend/
│   ├── arbolB.py               # Implementación del Árbol B
│   ├── lugar.py                # Modelo de datos Lugar
│   ├── grafo.py                # Estructura de grafos ponderados
│   ├── carga_csv.py            # Función para carga masiva desde CSV
├── static/
│   ├── css/                    # Estilos CSS
│   ├── js/                     # Scripts JavaScript
├── templates/
│   ├── index.html              # Página principal
│   ├── cargar.html             # Vista para carga masiva
│   ├── explorar.html           # Vista de lugares disponibles
│   ├── recomendaciones.html    # Vista de rutas recomendadas
├── data/
│   ├── datos.csv               # Archivo CSV de muestra
├── app.py                      # Servidor Flask principal
├── README.md                   # Este archivo

```

## 🧾 Formato del Archivo CSV

```bash
nombre,tipo,departamento,precio,calificacion
Tikal,turismo,Petén,100,4.7
Hotel Real,hospedaje,Zacapa,150,4.3

```
## 📌 Uso del Sistema
```bash
1. Cargar Lugares
Ir a la sección "Cargar Lugares"

Subir un archivo .csv

Verificar mensaje de éxito

2. Consultar Lugares
Ir a la sección "Explorar"

Filtrar por tipo, departamento o presupuesto

3. Calificar Lugar
Clic en un lugar

Ingresar nombre, puntuación y comentario

Enviar calificación

4. Obtener Recomendación
Ir a "Recomendar Ruta"

Ingresar origen, tiempo, presupuesto y tipo

Ver recomendaciones y ruta generada

5. Ver Mapa Interactivo
Clic en "Ver Mapa"

Se abre Google Maps con la ruta y marcadores


```
## 🔁 Rutas mediante Grafos Ponderados

```bash
El sistema genera rutas utilizando grafos ponderados, donde:

Los nodos representan lugares turísticos o de hospedaje.

Las aristas representan las conexiones entre lugares, con pesos (distancia, tiempo o costo).

Se utiliza el algoritmo de Dijkstra para encontrar la mejor ruta desde el origen.


```
## 🌳 Árboles de Rutas
```bash
TravelMap también genera internamente un árbol de decisiones:

Nodo raíz: lugar de origen.

Nodos hijos: rutas posibles hacia destinos.

Se filtran rutas según presupuesto, tiempo y tipo.

Ayuda a estructurar las recomendaciones que recibe el usuario.


```

## 🧠 Algoritmos y Estructuras Usadas
```bash
Árbol B: para almacenamiento eficiente de lugares

Grafo Ponderado: para modelar las conexiones entre destinos

Árbol de Decisión: para mostrar rutas desde un nodo base

Dijkstra: para encontrar rutas más óptimas


```
