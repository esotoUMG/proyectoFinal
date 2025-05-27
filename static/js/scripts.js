// --- Función para mostrar u ocultar el searchbar según la ruta ---
function toggleSearchbar(href) {
    const filtrosForm = document.getElementById('filtros-form');
    if (!filtrosForm) return;

    if (href === '/cargar') {
        filtrosForm.style.display = 'none';
    } else {
        filtrosForm.style.display = '';
    }
}

// --- Función para actualizar filtros según tipo de página ---
function actualizarFiltros(tipo) {
    const selectsContainer = document.getElementById('selects-container');
    const inputBusqueda = document.querySelector('#filtros-form input[name="busqueda"]');

    if (!selectsContainer || !inputBusqueda) return;

    if (tipo === "lugares") {
        selectsContainer.innerHTML = `
            <select name="tipo">
              <option value="">Tipo</option>
              <option value="playa">Playa</option>
              <option value="montaña">Montaña</option>
              <option value="monumento">Monumento</option>
            </select>
            <select name="precio">
              <option value="">Precio</option>
              <option value="economico">Económico</option>
              <option value="medio">Medio</option>
              <option value="lujo">Lujo</option>
            </select>
        `;
        inputBusqueda.placeholder = "Buscar lugares...";
    } else if (tipo === "hospedajes") {
        selectsContainer.innerHTML = `
            <select name="categoria">
              <option value="">Categoría</option>
              <option value="hotel">Hotel</option>
              <option value="hostel">Hostel</option>
              <option value="departamento">Departamento</option>
            </select>
            <select name="servicios">
              <option value="">Servicios</option>
              <option value="wifi">WiFi</option>
              <option value="desayuno">Desayuno</option>
              <option value="mascotas">Mascotas</option>
            </select>
        `;
        inputBusqueda.placeholder = "Buscar hospedajes...";
    } else {
        selectsContainer.innerHTML = '';
        inputBusqueda.placeholder = "Buscar...";
    }
}

// --- Función para cargar lugares desde la API y mostrarlos ---
function cargarLugaresDesdeAPI() {
    fetch('/api/lugares')
        .then(res => res.json())
        .then(data => {
            const lista = document.getElementById('lista-lugares');
            if (!lista) return;

            lista.innerHTML = ""; // Limpiar anterior

            data.lugares.forEach(lugar => {
                const item = document.createElement('div');
                item.classList.add('lugar-card');
                item.innerHTML = `
                    <h3>${lugar.nombre}</h3>
                    <p>Tipo: ${lugar.tipo}</p>
                    <p>Calificación: ${lugar.calificacion}</p>
                    <p>Tiempo de estadía: ${lugar.tiempo} horas</p>
                `;
                lista.appendChild(item);
            });
        })
        .catch(error => {
            console.error("Error al cargar lugares:", error);
        });
}

// --- Función para cargar contenido dinámicamente ---
function cargarContenido(e) {
    e.preventDefault();

    const enlace = e.currentTarget;
    const href = enlace.getAttribute('href');

    // Marcar el enlace como activo
    document.querySelectorAll('.opciones a, .anfitrion a').forEach(el => el.classList.remove('activo'));
    enlace.classList.add('activo');

    localStorage.setItem('pagina-activa', href);
    toggleSearchbar(href);

    if (href.includes("hospedajes")) {
        actualizarFiltros("hospedajes");
    } else if (href.includes("lugares")) {
        actualizarFiltros("lugares");
    } else {
        actualizarFiltros(null);
    }

    fetch(href)
        .then(response => {
            if (!response.ok) throw new Error("No se pudo cargar la página");
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const contenido = doc.querySelector('main#contenedor');
            if (contenido) {
                document.getElementById('contenedor').innerHTML = contenido.innerHTML;

                // 🔁 Volver a cargar los lugares desde la API si estamos en /lugares
                if (href.includes("lugares")) {
                    cargarLugaresDesdeAPI();
                }
            } else {
                throw new Error("No se encontró el contenido esperado");
            }
        })
        .catch(error => {
            document.getElementById('contenedor').innerHTML = "<p>Error al cargar contenido.</p>";
            console.error(error);
        });
}

// --- Agregar event listeners a enlaces del menú ---
document.querySelectorAll('.opciones a, .anfitrion a').forEach(link => {
    link.addEventListener('click', cargarContenido);
});

// --- Restaurar estado al recargar la página ---
window.addEventListener('DOMContentLoaded', () => {
    const activa = localStorage.getItem('pagina-activa') || window.location.pathname;
    const linkActivo = document.querySelector(`.opciones a[href="${activa}"], .anfitrion a[href="${activa}"]`);
    if (linkActivo) {
        linkActivo.classList.add('activo');
    }

    toggleSearchbar(activa);

    if (activa.includes("hospedajes")) {
        actualizarFiltros("hospedajes");
    } else if (activa.includes("lugares")) {
        actualizarFiltros("lugares");
        cargarLugaresDesdeAPI(); 
    } else {
        actualizarFiltros(null);
    }
});

// --- Manejo del scroll para fijar header ---
const header = document.querySelector('header');
const menu = document.querySelector('.menu.opciones');

window.addEventListener('scroll', () => {
    if (window.scrollY > 100) {
        header.classList.add('fixed');
    } else {
        header.classList.remove('fixed');
    }

    if (menu.classList.contains('menu-grande')) {
        menu.classList.remove('menu-grande');
    }
});
