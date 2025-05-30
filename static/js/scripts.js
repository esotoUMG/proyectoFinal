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

// --- Función para actualizar filtros según la ruta ---
function actualizarFiltros(tipo) {
    const filtrosForm = document.getElementById('filtros-form');
    if (!filtrosForm) return;

    if (tipo === 'lugares' || tipo === 'hospedajes') {
        filtrosForm.style.display = '';
    } else {
        filtrosForm.style.display = 'none';
    }
}

// --- Función común para procesar la respuesta fetch y actualizar el contenido ---
function procesarRespuestaFetch(href, html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const contenido = doc.querySelector('main#contenedor');
    if (contenido) {
        document.getElementById('contenedor').innerHTML = contenido.innerHTML;

        // Ejecutar funciones según la ruta actual
        if (href.includes("lugares") && typeof cargarLugaresDesdeAPI === 'function') {
            cargarLugaresDesdeAPI();
        } else if (href.includes("hospedajes") && typeof cargarHospedajesDesdeAPI === 'function') {
            cargarHospedajesDesdeAPI();
        }

        // --- NUEVO: Si la URL contiene detalle o filtro, cargar recomendaciones con presupuesto ---
        if (href.includes('/lugares/filtro/detalle') || href.includes('/lugares/filtro')) {
            cargarDetalleYRecomendacionesDesdeURL();
        }

    } else {
        console.error("No se encontró el contenido esperado en la respuesta");
        throw new Error("No se encontró el contenido esperado");
    }
}

// --- Función para cargar contenido dinámicamente desde un evento ---
function cargarContenido(e) {
    e.preventDefault();

    const enlace = e.currentTarget;
    const href = enlace.getAttribute('href');

    console.log("Click en enlace:", href);

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
            procesarRespuestaFetch(href, html);
            history.pushState({href: href}, '', href);  // Actualiza URL sin recargar
        })
        .catch(error => {
            const contenedor = document.getElementById('contenedor');
            if (contenedor) contenedor.innerHTML = "<p>Error al cargar contenido.</p>";
            console.error("Error en cargarContenido:", error);
        });
}

// --- Función para cargar contenido dinámicamente desde una ruta directa (sin evento) ---
function cargarContenidoDesdeRuta(href) {
    console.log("Navegando a:", href);

    document.querySelectorAll('.opciones a').forEach(el => el.classList.remove('activo'));
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
            procesarRespuestaFetch(href, html);
            history.pushState({href: href}, '', href);  // Actualiza URL sin recargar
        })
        .catch(error => {
            const contenedor = document.getElementById('contenedor');
            if (contenedor) contenedor.innerHTML = "<p>Error al cargar contenido.</p>";
            console.error("Error en cargarContenidoDesdeRuta:", error);
        });
}

// --- Manejo de eventos para retroceder y avanzar en historial con fetch ---
window.addEventListener('popstate', (event) => {
    if (event.state && event.state.href) {
        cargarContenidoDesdeRuta(event.state.href);
    }
});

// --- Fijar el header cuando el usuario haga scroll ---
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

// --- Cambiar la barra de navegación según la opción elegida y configurar formulario ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.startsWith('/lugares')) {
        actualizarFiltros('lugares');
    } else if (path.startsWith('/hospedajes')) {
        actualizarFiltros('hospedajes');
    } else {
        actualizarFiltros(null);
    }

    toggleSearchbar(path);

    const filtrosForm = document.getElementById('filtros-form');
    if (filtrosForm) {
        filtrosForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const path = window.location.pathname;  // Importante: obtener path actual aquí

            const formData = new FormData(filtrosForm);
            const busqueda = formData.get('busqueda')?.trim() || '';
            const presupuesto = formData.get('presupuesto')?.trim() || '';

            const params = new URLSearchParams();
            if (busqueda) params.append('busqueda', busqueda);
            if (presupuesto) params.append('presupuesto', presupuesto);

            let baseFiltro = '/lugares/filtro';
            if (path.startsWith('/hospedajes')) {
                baseFiltro = '/hospedajes/filtro';
            }

            const href = `${baseFiltro}?${params.toString()}`;
            cargarContenidoDesdeRuta(href);
        });
    }
});

// --- Bloquear zoom de la página web ---
window.addEventListener('wheel', function (e) {
    if (e.ctrlKey) {
        e.preventDefault();
    }
}, { passive: false });

window.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) &&
        (e.key === '+' || e.key === '-' || e.key === '=' || e.key === '_')) {
        e.preventDefault();
    }
});

window.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === '0') {
        e.preventDefault();
    }
});


// --- Función que lee presupuesto de URL y carga recomendaciones (ejemplo) ---
function cargarDetalleYRecomendacionesDesdeURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const presupuesto = urlParams.get('presupuesto');
    const nombre = urlParams.get('nombre');

    console.log("Presupuesto leído desde URL:", presupuesto);
    console.log("Nombre leído desde URL:", nombre);

    if (nombre && typeof cargarDetalleYRecomendaciones === 'function') {
        cargarDetalleYRecomendaciones(nombre);  // Esta función ya usa presupuesto de URL
    } else if (typeof cargarRecomendaciones === 'function') {
        // Por si quieres solo cargar recomendaciones sin detalle
        cargarRecomendaciones({ presupuesto: presupuesto });
    }
}
function asegurarPresupuestoEnURL() {
    const rutaActual = window.location.pathname;

    // Solo ejecutar en las rutas donde sí es necesario el presupuesto
    const rutasQueUsanPresupuesto = ['/lugares/detalle', '/lugares/filtro/detalle'];

    if (!rutasQueUsanPresupuesto.includes(rutaActual)) {
        return;  // No hacer nada si no estamos en una ruta que lo necesita
    }

    const urlParams = new URLSearchParams(window.location.search);

    if (!urlParams.has('presupuesto')) {
        const inputPresupuesto = document.getElementById('inputPresupuesto');
        let presupuestoInput = inputPresupuesto ? inputPresupuesto.value : '';

        if (!presupuestoInput || isNaN(presupuestoInput)) {
            presupuestoInput = '10000';
        }

        urlParams.set('presupuesto', presupuestoInput);
        const nuevaURL = `${window.location.pathname}?${urlParams.toString()}`;
        window.history.replaceState(null, '', nuevaURL);
        console.log("Se agregó presupuesto en URL:", nuevaURL);
    }
}

asegurarPresupuestoEnURL();



// --- Ejemplo de función cargarRecomendaciones ---
function cargarRecomendaciones({ presupuesto }) {
    // Ejemplo simple para llamar a la API con presupuesto
    fetch(`/api/recomendaciones?presupuesto=${encodeURIComponent(presupuesto)}`)
        .then(res => res.json())
        .then(data => {
            console.log("Recomendaciones recibidas:", data);
            // Actualizar DOM con recomendaciones recibidas
        })
        .catch(err => {
            console.error("Error al cargar recomendaciones:", err);
        });
}
