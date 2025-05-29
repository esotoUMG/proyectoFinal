document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const nombre = urlParams.get('nombre');  // Obtener nombre de la URL

    // Si estamos en página detalle (tiene ?nombre=...), carga el detalle y recomendaciones
    if (nombre) {
        cargarDetalleYRecomendaciones(nombre);
    }

    // Agrega listeners a las tarjetas principales si existen (lista de lugares)
    agregarListenerTarjetasPrincipales();
});

function cargarDetalleYRecomendaciones(nombre) {
    fetch(`/api/hospedaje?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.lugar) {
                mostrarInfoLugar(data.lugar);
            } else {
                console.error("No se encontró el lugar en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener lugar:", err));

    fetch(`/api/recomendaciones_hospedajes?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.recomendaciones) {
                mostrarRecomendaciones(data.recomendaciones);
            } else {
                console.error("No se encontraron recomendaciones en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener recomendaciones:", err));
}

function mostrarInfoLugar(lugar) {
    const contenedor = document.getElementById('info-detallada');
    if (!contenedor) {
        console.error("No se encontró el contenedor info-detallada");
        return;
    }

    contenedor.innerHTML = `
        <h2>${lugar.nombre}</h2>
        <p><strong>Dirección:</strong> ${lugar.direccion}</p>
        <p><strong>Ubicación:</strong> ${lugar.municipio}, ${lugar.departamento}</p>
        <p><strong>Tipo:</strong> ${lugar.tipo}</p>
        <p><strong>Calificación:</strong> ${lugar.calificacion}</p>
    `;

    // Llama manualmente a initMap para volver a inicializar el mapa
    if (typeof initMap === "function") {
        initMap();
    } else {
        console.error("initMap no está definida");
    }
}


function mostrarRecomendaciones(recomendaciones) {
    const contenedor = document.getElementById('recomendaciones-cercanas');
    if (!contenedor) {
        console.error("No se encontró el contenedor recomendaciones-cercanas");
        return;
    }

    contenedor.innerHTML = `<h3>Recomendaciones cercanas</h3>`;

    if (!recomendaciones.length) {
        contenedor.innerHTML += `<p>No se encontraron recomendaciones cercanas.</p>`;
        return;
    }

    const lista = document.createElement('div');
    lista.classList.add('recomendaciones-grid');

    recomendaciones.slice(0, 5).forEach(lugar => {
        const card = document.createElement('div');
        card.classList.add('recomendaciones-card');
        card.innerHTML = `
            <h4>${lugar.nombre}</h4>
            <p>${lugar.direccion}</p>
            <p>${lugar.municipio}, ${lugar.departamento}</p>
            <p>Calificación: ${lugar.calificacion}</p>
        `;

        card.addEventListener('click', () => {
            redirigirADetalleConFiltros(lugar.nombre);
        });

        lista.appendChild(card);
    });

    contenedor.appendChild(lista);
}

function agregarListenerTarjetasPrincipales() {
    // Selecciona todas las tarjetas de la lista principal (asegúrate que tengan la clase lugar-card)
    const tarjetas = document.querySelectorAll('.lugar-card');
    if (!tarjetas.length) return;

    tarjetas.forEach(card => {
        card.addEventListener('click', () => {
            const nombreLugar = card.getAttribute('data-nombre');
            if (!nombreLugar) {
                console.error("La tarjeta no tiene atributo data-nombre");
                return;
            }
            redirigirADetalleConFiltros(nombreLugar);
        });
    });
}

function redirigirADetalleConFiltros(nombreLugar) {
    const nombreEncoded = encodeURIComponent(nombreLugar);
    const path = window.location.pathname;
    const queryString = window.location.search; // Ejemplo: "?tipo=Comida&departamento=Guatemala"

    let urlDetalle;
    if (path.startsWith('/hospedajes/filtro')) {
        // Quita el '?' inicial para concatenar
        const filtros = queryString.length > 0 ? queryString.substring(1) : "";
        // Usa ruta detalle estándar (cambia si tienes ruta especial)
        urlDetalle = `/hospedajes/detalle?nombre=${nombreEncoded}`;
        if (filtros) {
            urlDetalle += `&${filtros}`;
        }
    } else {
        urlDetalle = `/hospedajes/detalle?nombre=${nombreEncoded}`;
    }

    window.location.href = urlDetalle;
}
