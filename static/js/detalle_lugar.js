document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const nombre = urlParams.get('nombre');
    const idx = urlParams.get('idx');

    if (nombre) {
        cargarDetalle(nombre);
    } else if (idx !== null && idx !== '') {
        fetch(`/lugares/detalle/${idx}`)
            .then(res => res.ok ? res.json() : Promise.reject(res.status))
            .then(data => {
                if (data.lugar) {
                    mostrarInfoLugar(data.lugar);
                    cargarRecomendaciones(data.lugar.nombre);
                } else {
                    mostrarMensajeGrafo("No se encontró el lugar", "error");
                }
            })
            .catch(err => {
                console.error("Error al obtener detalle:", err);
                mostrarMensajeGrafo("Error al obtener datos", "error");
            });
    } else {
        mostrarMensajeGrafo("No se especificó un lugar. Por favor, seleccione uno.", "advertencia");
        const contenedor = document.getElementById('info-detallada');
        if (contenedor) contenedor.innerHTML = '<p>No se ha especificado ningún lugar para mostrar.</p>';
    }
});

function cargarDetalle(nombre) {
    fetch(`/api/lugar?nombre=${encodeURIComponent(nombre)}`)
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(data => {
            if (data.lugar) {
                mostrarInfoLugar(data.lugar);
                cargarRecomendaciones(data.lugar.nombre);
            } else {
                mostrarMensajeGrafo("Lugar no encontrado", "error");
            }
        })
        .catch(err => {
            console.error("Error al obtener lugar:", err);
            mostrarMensajeGrafo("Error al obtener lugar", "error");
        });
}

function cargarRecomendaciones(nombre) {
    const urlParams = new URLSearchParams(window.location.search);
    const presupuesto = urlParams.get('presupuesto') || '10000';
    const tiempoMaxDiario = urlParams.get('tiempo_max_diario') || '8';

    fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombre)}&presupuesto=${presupuesto}&tiempo_max_diario=${tiempoMaxDiario}`)
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(data => {
            if (data.recomendaciones) {
                mostrarRecomendaciones(data.recomendaciones, nombre);
            } else {
                mostrarMensajeGrafo("Sin recomendaciones disponibles", "advertencia");
            }
        })
        .catch(err => {
            console.error("Error al obtener recomendaciones:", err);
            mostrarMensajeGrafo("Error al obtener recomendaciones", "error");
        });
}

function mostrarInfoLugar(lugar) {
    const contenedor = document.getElementById('info-detallada');
    if (!contenedor) return;

    const precio = Number(lugar.precio) === 0 ? 'Gratis' : `Q ${Number(lugar.precio).toFixed(2)}`;
    const calificacion = Number(lugar.calificacion) || 0;
    const estrellas = generarEstrellasHTML(calificacion);

    contenedor.innerHTML = `
        <h2>${lugar.nombre}</h2>
        <p>${lugar.direccion}</p>
        <p>${lugar.municipio}, ${lugar.departamento}</p>
        <p>${lugar.tipo}</p>
        <p><span class="calificacion-valor">${calificacion.toFixed(1)}</span>
        <span class="estrellas">${estrellas}</span></p>
        <p>${precio}</p>
    `;

    if (typeof initMap === "function") {
        initMap();
    }
}

function mostrarRecomendaciones(recomendaciones, nodoPrincipal) {
    const contenedor = document.getElementById('recomendaciones-cercanas');
    if (!contenedor) return;

    contenedor.innerHTML = `<h3>Recomendaciones cercanas</h3>`;

    if (!recomendaciones.length) {
        contenedor.innerHTML += `<p class="recomendaciones">No se encontraron recomendaciones cercanas.</p>`;
        return;
    }

    const lista = document.createElement('div');
    lista.classList.add('recomendaciones-grid');

    const nombresUnicos = new Set();
    recomendaciones.slice(0, 5).forEach(lugar => {
        if (nombresUnicos.has(lugar.nombre)) return;
        nombresUnicos.add(lugar.nombre);

        const calificacion = Number(lugar.calificacion) || 0;
        const precio = Number(lugar.precio) || 0;
        const tiempoEstadia = Number(lugar.tiempo_estadia) || 0;
        const tiempoTraslado = Number(lugar.tiempo_traslado) || 0;
        const tiempoTrasladoStr = lugar.tiempo_traslado_str || formatoHorasMinutos(tiempoTraslado);
        const estrellas = generarEstrellasHTML(calificacion);

        const card = document.createElement('div');
        card.classList.add('recomendaciones-card');
        card.setAttribute('data-nombre', lugar.nombre);

        card.innerHTML = `
            <h4>${lugar.nombre}</h4>
            <p>${lugar.direccion}</p>
            <p>${lugar.municipio}, ${lugar.departamento}</p>
            <p>
                Calificación: <span class="calificacion-valor">${calificacion.toFixed(1)}</span>
                <span class="estrellas">${estrellas}</span>
            </p>
            <p>Precio: ${precio === 0 ? 'Gratis' : `Q ${precio.toFixed(2)}`}</p>
            <p>Tiempo de estadía: ${tiempoEstadia.toFixed(1)} hrs</p>
            <p>Tiempo aproximado de traslado: ${tiempoTrasladoStr}</p>
            <p><strong>Tiempo total aproximado:</strong> ${formatoHorasMinutos(tiempoEstadia + tiempoTraslado)}</p>
        `;

        card.addEventListener('click', () => redirigirADetalleConFiltros(lugar.nombre));
        lista.appendChild(card);
    });

    contenedor.appendChild(lista);

    const grafo = construirGrafoDesdeRecomendaciones(nodoPrincipal, recomendaciones.slice(0, 5));
    const idGrafo = Date.now();
    enviarGrafoAlBackend(grafo, idGrafo);
}

function generarEstrellasHTML(calificacion) {
    let estrellas = '';
    for (let i = 1; i <= 5; i++) {
        if (calificacion >= i) {
            estrellas += '<span class="estrella llena">&#9733;</span>';
        } else if (calificacion >= i - 0.5) {
            estrellas += '<span class="estrella media">&#9733;</span>';
        } else {
            estrellas += '<span class="estrella vacia">&#9734;</span>';
        }
    }
    return estrellas;
}

function formatoHorasMinutos(horas) {
    if (isNaN(horas) || horas <= 0) return "0 mins";
    const h = Math.floor(horas);
    const m = Math.round((horas - h) * 60);
    if (h > 0 && m > 0) return `${h} hrs ${m} mins`;
    if (h > 0) return `${h} hrs`;
    return `${m} mins`;
}

function redirigirADetalleConFiltros(nombreLugar) {
    const path = window.location.pathname;
    const urlParams = new URLSearchParams(window.location.search);

    const presupuesto = document.getElementById('inputPresupuesto')?.value || '10000';
    const tiempoMax = document.getElementById('inputTiempoMaxDiario')?.value || '8';
    const star = urlParams.get('star') || '';

    const nuevosParams = new URLSearchParams();
    for (const [key, value] of urlParams.entries()) {
        if (!['nombre', 'presupuesto', 'tiempo_max_diario'].includes(key)) {
            nuevosParams.append(key, value);
        }
    }

    nuevosParams.set('nombre', nombreLugar);
    nuevosParams.set('presupuesto', presupuesto);
    nuevosParams.set('tiempo_max_diario', tiempoMax);
    if (star) nuevosParams.set('star', star);

    const url = path.startsWith('/lugares/filtro')
        ? `/lugares/filtro/detalle?${nuevosParams}`
        : `/lugares/detalle?${nuevosParams}`;

    window.location.href = url;
}

function construirGrafoDesdeRecomendaciones(nodoPrincipal, recomendaciones) {
    const nodos = [nodoPrincipal];
    const aristas = [];

    recomendaciones.forEach(r => {
        if (r.nombre && r.nombre !== nodoPrincipal) {
            nodos.push(r.nombre);
            const tiempoMin = (Number(r.tiempo_traslado) || 0) * 60;
            aristas.push({ origen: nodoPrincipal, destino: r.nombre, peso: tiempoMin });
        }
    });

    return { nodos, aristas };
}

function mostrarMensajeGrafo(texto, tipo = 'exito') {
    const contenedor = document.getElementById('mensaje-grafo');
    if (!contenedor) return;

    contenedor.style.display = 'block';
    contenedor.textContent = texto;

    const estilos = {
        exito: ['#d4edda', '#155724', '#c3e6cb'],
        error: ['#f8d7da', '#721c24', '#f5c6cb'],
        advertencia: ['#fff3cd', '#856404', '#ffeeba']
    };

    const [bg, color, border] = estilos[tipo] || estilos.exito;
    contenedor.style.backgroundColor = bg;
    contenedor.style.color = color;
    contenedor.style.border = `1px solid ${border}`;

    setTimeout(() => { contenedor.style.display = 'none'; }, 4000);
}

function enviarGrafoAlBackend(grafo, idGrafo) {
    const aristasConvertidas = grafo.aristas.map(a => ({
        origen: a.origen,
        destino: a.destino,
        peso: Number(a.peso) || 1
    }));

    fetch('/api/generar_grafo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: idGrafo, nodos: grafo.nodos, aristas: aristasConvertidas })
    })
    .then(res => res.ok ? res.json() : Promise.reject(res.status))
    .then(data => console.log('Grafo guardado:', data.rutaArchivo))
    .catch(err => console.error('Error al enviar grafo:', err));
}
