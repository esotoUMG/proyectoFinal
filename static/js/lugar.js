document.addEventListener('DOMContentLoaded', () => {
    // Solo cargar lugares si estamos en la página de lugares (evitar llamada innecesaria)
    if (window.location.pathname.includes('lugares')) {
        cargarLugaresDesdeAPI();
    }
});

// --- Función para cargar lugares desde la API y mostrarlos ---
function cargarLugaresDesdeAPI() {
    console.log("Cargando lugares...");

    fetch('/api/lugares')
        .then(res => {
            if (!res.ok) throw new Error('Error en la respuesta de la API');
            return res.json();
        })
        .then(data => {
            // Cambié el id aquí porque ahora usaremos un contenedor principal donde se pondrán las secciones
            const mainContenedor = document.getElementById('contenedor');
            if (!mainContenedor) {
                console.warn("No se encontró el contenedor 'contenedor'");
                return;
            }

            mainContenedor.innerHTML = ""; // Limpiar contenido previo

            if (!data.lugares || data.lugares.length === 0) {
                mainContenedor.innerHTML = "<p>No hay lugares disponibles.</p>";
                return;
            }

            // Filtrar y ordenar según los tipos que vienen en el CSV
            const comida = data.lugares
                .filter(l => l.tipo === 'Comida')
                .sort((a, b) => b.calificacion - a.calificacion);

            const entretenimiento = data.lugares.filter(l => l.tipo === 'Entretenimiento');
            const turismo = data.lugares.filter(l => l.tipo === 'Turismo');

            // Crear y agregar secciones carrusel sólo si hay datos en esa categoría
            if (comida.length > 0) {
                mainContenedor.appendChild(crearSeccionCarrusel("Recomendación de Restaurantes", comida));
            }
            if (entretenimiento.length > 0) {
                mainContenedor.appendChild(crearSeccionCarrusel("Recomendación de Lugares Recreativos", entretenimiento));
            }
            if (turismo.length > 0) {
                mainContenedor.appendChild(crearSeccionCarrusel("Recomendación de Lugares Turísticos", turismo));
            }
        })
        .catch(error => {
            console.error("Error al cargar lugares:", error);
            const mainContenedor = document.getElementById('contenedor');
            if (mainContenedor) mainContenedor.innerHTML = "<p>Error al cargar lugares.</p>";
        });
}

// --- Función para crear una sección tipo carrusel con flechas ---
function crearSeccionCarrusel(titulo, lugares) {
    // Crear contenedor general
    const contenedor = document.createElement('div');
    contenedor.classList.add('carrusel-container');
  
    // Crear título
    const h2 = document.createElement('h2');
    h2.classList.add('carrusel-titulo');
    h2.textContent = titulo;
  
    // Crear flechas para navegar
    const btnIzq = document.createElement('button');
    btnIzq.classList.add('flecha', 'izquierda');
    btnIzq.setAttribute('aria-label', 'Anterior');
    btnIzq.innerHTML = '&#8592;';
  
    const btnDer = document.createElement('button');
    btnDer.classList.add('flecha', 'derecha');
    btnDer.setAttribute('aria-label', 'Siguiente');
    btnDer.innerHTML = '&#8594;';
  
    // Crear contenedor horizontal scrollable
    const carrusel = document.createElement('div');
    carrusel.classList.add('carrusel');
  
    // Crear las tarjetas de lugares
    lugares.forEach(lugar => {
      const item = document.createElement('div');
      item.classList.add('lugar-card');
      item.innerHTML = `
        <h3>${lugar.nombre}</h3>
        <p>Tipo: ${lugar.tipo}</p>
        <p>Dirección: ${lugar.direccion}</p>
        <p>Calificación: ${lugar.calificacion}</p>
      `;
      carrusel.appendChild(item);
    });
  
    // Agregar elementos al contenedor principal de la sección
    contenedor.appendChild(h2);
    contenedor.appendChild(btnIzq);
    contenedor.appendChild(carrusel);
    contenedor.appendChild(btnDer);
  
    // Agregar funcionalidad flechas para hacer scroll horizontal suave
    btnIzq.addEventListener('click', () => {
      carrusel.scrollBy({ left: -250, behavior: 'smooth' });
    });
    btnDer.addEventListener('click', () => {
      carrusel.scrollBy({ left: 250, behavior: 'smooth' });
    });
  
    return contenedor;
}
