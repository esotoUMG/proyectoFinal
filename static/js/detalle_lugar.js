document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const nombre = urlParams.get('nombre');  // Obtener nombre de la URL

    if (!nombre) {
        console.error("No se proporcionó un nombre en la URL");
        return;
    }

    // Llamar API lugar
    fetch(`/api/lugar?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log("Detalle lugar recibido:", data);
            if (data.lugar) {
                mostrarInfoLugar(data.lugar);
            } else {
                console.error("No se encontró el lugar en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener lugar:", err));

    // Llamar API recomendaciones
    fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log("Recomendaciones recibidas:", data);
            if (data.recomendaciones) {
                mostrarRecomendaciones(data.recomendaciones);
            } else {
                console.error("No se encontraron recomendaciones en la respuesta");
            }
        })
        .catch(err => console.error("Error al obtener recomendaciones:", err));
});

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
            const nombreEncoded = encodeURIComponent(lugar.nombre);
            window.location.href = `/lugares/detalle?nombre=${nombreEncoded}`;
        });

        lista.appendChild(card);
    });

    contenedor.appendChild(lista);
}
