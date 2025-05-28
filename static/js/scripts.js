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

// --- Función para cargar contenido dinámicamente ---
function cargarContenido(e) {
    e.preventDefault();

    const enlace = e.currentTarget;
    const href = enlace.getAttribute('href');

    console.log("Click en enlace:", href);

    // Marcar enlace activo
    document.querySelectorAll('.opciones a').forEach(el => el.classList.remove('activo'));
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
            console.log("Fetch response status:", response.status);
            if (!response.ok) throw new Error("No se pudo cargar la página");
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const contenido = doc.querySelector('main#contenedor');
            if (contenido) {
                document.getElementById('contenedor').innerHTML = contenido.innerHTML;

                if (href.includes("lugares")) {
                    cargarLugaresDesdeAPI();
                } else if (href.includes("hospedajes")) {
                    cargarHospedajesDesdeAPI();
                }
            } else {
                console.error("No se encontró el contenido esperado en la respuesta");
                throw new Error("No se encontró el contenido esperado");
            }
        })
        .catch(error => {
            const contenedor = document.getElementById('contenedor');
            if (contenedor) contenedor.innerHTML = "<p>Error al cargar contenido.</p>";
            console.error("Error en cargarContenido:", error);
        });
}


// --- Función para actualizar filtros según tipo de página ---
function actualizarFiltros(tipo) {
    const selectsContainer = document.getElementById('selects-container');
    const inputBusqueda = document.querySelector('#filtros-form input[name="busqueda"]');

    if (!selectsContainer || !inputBusqueda) return;

    selectsContainer.innerHTML = '';
    inputBusqueda.classList.remove('lugares-style', 'hospedajes-style');

    if (tipo === "lugares") {
        selectsContainer.innerHTML = `
            <select name="tipo">
              <option value="">Tipo</option>
              <option value="playa">Comida</option>
              <option value="montaña">Entretenimiento</option>
              <option value="monumento">Turismo</option>
            </select>
            <select name="precio">
              <option value="">Precio</option>
              <option value="economico">Económico</option>
              <option value="medio">Medio</option>
              <option value="lujo">Lujo</option>
            </select>
        `;
        inputBusqueda.placeholder = "Buscar lugares...";
        inputBusqueda.classList.add('lugares-style');
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
        inputBusqueda.classList.add('hospedajes-style');
    } else {
        inputBusqueda.placeholder = "Buscar...";
    }
}

//FIJAR EL HEADER CUANDO EL USUARIO HAGA SCROLL
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

//CAMBIAR LA BARRA DE NAVEGACION SEGUN LA OPCION QUE HAYA ELEGIDO EL USUARIO
document.addEventListener('DOMContentLoaded', () => {
    // Obtener la ruta actual
    const path = window.location.pathname;

    if (path.startsWith('/lugares')) {
        actualizarFiltros('lugares');
    } else if (path.startsWith('/hospedajes')) {
        actualizarFiltros('hospedajes');
    } else {
        actualizarFiltros(null);
    }

    // Mostrar u ocultar el searchbar si vas a /cargar
    toggleSearchbar(path);
});

//BLOQUEAR EL ZOOM DE LA PAGINA WEB 
// Bloquear zoom con Ctrl + scroll del mouse
window.addEventListener('wheel', function(e) {
    if (e.ctrlKey) {
        e.preventDefault();
    }
}, { passive: false });

// Bloquear zoom con Ctrl + '+' o Ctrl + '-'
window.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && 
        (e.key === '+' || e.key === '-' || e.key === '=' || e.key === '_')) {
        e.preventDefault();
    }
});

// Opcional: bloquear Ctrl + 0 (reset zoom)
window.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === '0') {
        e.preventDefault();
    }
});
