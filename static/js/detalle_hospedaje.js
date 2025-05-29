document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const nombre = urlParams.get('nombre');  // Obtener nombre de la URL

    if (!nombre) {
        console.error("No se proporcionó un nombre en la URL");
        return;
    }

    fetch(`/api/hospedaje?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.hospedaje) {
                mostrarInfoHospedaje(data.hospedaje);
                if (typeof initMap === "function") {
                    initMap(); // Si tienes mapa con coordenadas reales
                }
            } else {
                console.error("No se encontró el hospedaje en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener hospedaje:", err));

    fetch(`/api/recomendaciones-hospedaje?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.recomendaciones) {
                mostrarRecomendacionesHospedaje(data.recomendaciones);
            } else {
                console.error("No se encontraron recomendaciones en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener recomendaciones:", err));
});

function mostrarInfoHospedaje(hospedaje) {
    const contenedor = document.getElementById('info-detallada-hospedaje');
    if (!contenedor) {
        console.error("No se encontró el contenedor info-detallada-hospedaje");
        return;
    }
    contenedor.innerHTML = `
        <h2>${hospedaje.nombre}</h2>
        <p><strong>Dirección:</strong> ${hospedaje.direccion}</p>
        <p><strong>Ubicación:</strong> ${hospedaje.municipio}, ${hospedaje.departamento}</p>
        <p><strong>Tipo:</strong> ${hospedaje.tipo}</p>
        <p><strong>Calificación:</strong> ${hospedaje.calificacion}</p>
    `;
}

function mostrarRecomendacionesHospedaje(recomendaciones) {
    const contenedor = document.getElementById('recomendaciones-cercanas-hospedaje');
    if (!contenedor) {
        console.error("No se encontró el contenedor recomendaciones-cercanas-hospedaje");
        return;
    }

    contenedor.innerHTML = `<h3>Recomendaciones de hospedajes cercanos</h3>`;

    if (!recomendaciones.length) {
        contenedor.innerHTML += `<p>No se encontraron recomendaciones cercanas.</p>`;
        return;
    }

    const lista = document.createElement('div');
    lista.classList.add('recomendaciones-grid');

    recomendaciones.slice(0, 5).forEach(hospedaje => {
        const card = document.createElement('div');
        card.classList.add('recomendaciones-card');
        card.innerHTML = `
            <h4>${hospedaje.nombre}</h4>
            <p>${hospedaje.direccion}</p>
            <p>${hospedaje.municipio}, ${hospedaje.departamento}</p>
            <p>Calificación: ${hospedaje.calificacion}</p>
        `;

        card.addEventListener('click', () => {
            const nombreEncoded = encodeURIComponent(hospedaje.nombre);
            window.location.href = `/hospedajes/detalle?nombre=${nombreEncoded}`;
        });

        lista.appendChild(card);
    });

    contenedor.appendChild(lista);
}
