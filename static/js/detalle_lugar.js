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
    fetch(`/api/lugar?nombre=${encodeURIComponent(nombre)}`)
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

    fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombre)}`)
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

    const precio = lugar.precio === 0 ? 'Gratis' : `Desde Q ${lugar.precio}`
    const calificacion = lugar.calificacion
    const estrellas = generarEstrellasHTML(calificacion)

    contenedor.innerHTML = `
        <h2>${lugar.nombre}</h2>
        <p> ${lugar.direccion}</p>
        <p> ${lugar.municipio}, ${lugar.departamento}</p>
        <p> ${lugar.tipo}</p>
        <p>
            <span class="calificacion-valor">${calificacion.toFixed(1)}</span>
            <span class="estrellas">${estrellas}</span>
        </p>
        <p>${precio}</p>
    `;

    // Llama manualmente a initMap para volver a inicializar el mapa
    if (typeof initMap === "function") {
        initMap();
    } else {
        console.error("initMap no está definida");
    }
}

    // Función auxiliar para generar estrellas según la calificación
    const generarEstrellasHTML = (calificacion) => {

        const maxEstrellas = 5;
        let estrellas = '';

        for (let i = 1; i <= maxEstrellas; i++) {
            if (calificacion >= i) {
                // estrella llena
                estrellas += '<span class="estrella llena">&#9733;</span>';
            } else if (calificacion >= i - 0.5) {
                // estrella media
                estrellas += '<span class="estrella media">&#9733;</span>';
            } else {
                // estrella vacía
                estrellas += '<span class="estrella vacia">&#9734;</span>';
            }
        }

        return estrellas;
    };

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

        lista.appendChild(card);
    });

    contenedor.appendChild(lista);
}


function agregarListenerTarjetasPrincipales() {
    // Selecciona todas las tarjetas de la lista principal (asegúrate que tengan la clase lugar-card)
    const tarjetas = document.querySelectorAll('.recomendaciones-card');
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
    const queryString = window.location.search; 

    let urlDetalle;

    if (path.startsWith('/lugares/filtro')) {
        const filtros = queryString.length > 0 ? queryString.substring(1) : "";
        urlDetalle = `/lugares/filtro/detalle?nombre=${nombreEncoded}`;
        if (filtros) {
            urlDetalle += `&${filtros}`;
        }
    } else {
        // Ruta detalle normal
        urlDetalle = `/lugares/detalle?nombre=${nombreEncoded}`;
    }

    console.log("Redirigiendo a:", urlDetalle);
    window.location.href = urlDetalle;
}

