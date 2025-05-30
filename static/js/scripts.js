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

// --- Función para cargar contenido dinámicamente (solo para enlaces) ---
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

// --- Evento DOMContentLoaded ---
document.addEventListener('DOMContentLoaded', () => {
    // Asignar cargarContenido SOLO a enlaces de navegación dentro de .opciones
    document.querySelectorAll('.opciones a').forEach(link => {
        link.addEventListener('click', cargarContenido);
    });

    // Manejar submit del formulario de filtros
    const filtrosForm = document.getElementById('filtros-form');
    if (filtrosForm) {
        filtrosForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const formData = new FormData(filtrosForm);
            const busqueda = formData.get('busqueda').trim();
            const presupuesto = formData.get('presupuesto').trim();

            const params = new URLSearchParams();
            if (busqueda) params.append('departamento', busqueda);
            if (presupuesto) params.append('presupuesto', presupuesto);

            // Redirigir a la página de filtro con parámetros
            window.location.href = `/lugares/filtro?${params.toString()}`;
        });
    }

    // Mostrar u ocultar el searchbar según la ruta actual
    const path = window.location.pathname;
    toggleSearchbar(path);

    // Actualizar filtros según la ruta
    if (path.startsWith('/lugares')) {
        actualizarFiltros('lugares');
    } else if (path.startsWith('/hospedajes')) {
        actualizarFiltros('hospedajes');
    } else {
        actualizarFiltros(null);
    }
});

// FIJAR EL HEADER CUANDO EL USUARIO HAGA SCROLL
const header = document.querySelector('header');
const menu = document.querySelector('.menu.opciones');

window.addEventListener('scroll', () => {
    if (window.scrollY > 150) {
        header.classList.add('fixed');
    } else {
        header.classList.remove('fixed');
    }

    if (menu.classList.contains('menu-grande')) {
        menu.classList.remove('menu-grande');
    }
});

// BLOQUEAR EL ZOOM DE LA PAGINA WEB 
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
