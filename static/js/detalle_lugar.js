document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const nombre = urlParams.get('nombre');  // Obtener nombre de la URL

    if (nombre) {
        cargarDetalleYRecomendaciones(nombre);
    }

    agregarListenerTarjetasPrincipales();
});

function cargarDetalleYRecomendaciones(nombre) {
    const urlParams = new URLSearchParams(window.location.search);
    const presupuesto = urlParams.get('presupuesto') || 10000;
    const tiempoMaxDiario = urlParams.get('tiempo_max_diario') || 8;

    // Cargar info del lugar principal
    fetch(`/api/lugar?nombre=${encodeURIComponent(nombre)}`)
        .then(res => {
        if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
        return res.json();
        })
        .then(data => {
        if (data.lugar) {
            mostrarInfoLugar(data.lugar);
            window.idLugarActual = data.lugar.id;  // <=== Guarda aquí el id del lugar
            cargarCalificaciones(window.idLugarActual); // carga las calificaciones con ese id
            console.log("Respuesta del API /api/lugar:", data);
        } else {
            console.error("No se encontró el lugar en la respuesta");
        }
        })
        .catch(err => console.error("Error al obtener lugar:", err));
    

    // Cargar recomendaciones con filtros presupuesto y tiempo máximo
    fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombre)}&presupuesto=${presupuesto}&tiempo_max_diario=${tiempoMaxDiario}`)
        .then(res => {
            if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.recomendaciones) {
                mostrarRecomendaciones(data.recomendaciones, nombre);
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

    const precio = Number(lugar.precio) === 0 ? 'Gratis' : ` Q ${Number(lugar.precio).toFixed(2)}`;
    const calificacion = Number(lugar.calificacion) || 0;
    const estrellas = generarEstrellasHTML(calificacion);

    contenedor.innerHTML = `
        <h2>${lugar.nombre}</h2>
        <p>${lugar.direccion}</p>
        <p>${lugar.municipio}, ${lugar.departamento}</p>
        <p>${lugar.tipo}</p>
        <p>
            <span class="calificacion-valor">${calificacion.toFixed(1)}</span>
            <span class="estrellas">${estrellas}</span>
        </p>
        <p>${precio}</p>
    `;

    if (typeof initMap === "function") {
        initMap();
    } else {
        console.error("initMap no está definida");
    }
}

function generarEstrellasHTML(calificacion) {
    const maxEstrellas = 5;
    let estrellas = '';

    for (let i = 1; i <= maxEstrellas; i++) {
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

function mostrarRecomendaciones(recomendaciones, nodoPrincipal) {
    const contenedor = document.getElementById('recomendaciones-cercanas');
    if (!contenedor) {
        console.error("No se encontró el contenedor recomendaciones-cercanas");
        return;
    }

    contenedor.innerHTML = `<h3>Recomendaciones cercanas</h3>`;

    if (!recomendaciones.length) {
        contenedor.innerHTML += `<p class="recomendaciones">No se encontraron recomendaciones cercanas.</p>`;
        return;
    }

    const lista = document.createElement('div');
    lista.classList.add('recomendaciones-grid');

    recomendaciones.slice(0, 5).forEach(lugar => {
        const calificacion = Number(lugar.calificacion) || 0;
        const precio = Number(lugar.precio) || 0;
        const tiempoEstadia = Number(lugar.tiempo_estadia) || 0;
        const tiempoTraslado = Number(lugar.tiempo_traslado) || 0;
        const tiempoTotal = tiempoEstadia + tiempoTraslado;
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
            <p>Precio: ${precio === 0 ? 'Gratis' : ` Q ${precio.toFixed(2)}`}</p>
            <p>Tiempo de estadía: ${tiempoEstadia.toFixed(1)} hrs</p>
            <p>Tiempo aproximado de traslado: ${tiempoTrasladoStr}</p>
            <p><strong>Tiempo total aproximado:</strong> ${formatoHorasMinutos(tiempoTotal)}</p>
        `;

        card.addEventListener('click', () => {
            const nombreLugar = card.getAttribute('data-nombre');
            if (typeof window.seleccionarLugarRecomendado === 'function') {
                window.seleccionarLugarRecomendado(nombreLugar);
            }
        });

        lista.appendChild(card);
    });

    contenedor.appendChild(lista);

    // Construir y enviar grafo automáticamente
    // const grafo = construirGrafoDesdeRecomendaciones(nodoPrincipal, recomendaciones.slice(0, 5));
    // const idGrafo = Date.now();
    // enviarGrafoAlBackend(grafo, idGrafo);
    // Crear botón para generar grafo


    const botonGenerarGrafo = document.createElement('button');
    botonGenerarGrafo.textContent = 'Generar Grafo';
    botonGenerarGrafo.id = 'btn-generar-grafo';

    // Evita crear varios botones si ya existe
    if (!document.getElementById('btn-generar-grafo')) {
        contenedor.appendChild(botonGenerarGrafo);
    }

    botonGenerarGrafo.addEventListener('click', () => {
        const grafo = construirGrafoDesdeRecomendaciones(nodoPrincipal, recomendaciones.slice(0, 5));
        const idGrafo = Date.now();
        enviarGrafoAlBackend(grafo, idGrafo);
        mostrarMensajeGrafo('Grafo generado y enviado al backend.');
    });

}

function formatoHorasMinutos(horas) {
    if (isNaN(horas) || horas <= 0) return "0 mins";
    const h = Math.floor(horas);
    const m = Math.round((horas - h) * 60);
    if (h > 0 && m > 0) return `${h} hrs ${m} mins`;
    if (h > 0) return `${h} hrs`;
    return `${m} mins`;
}

function agregarListenerTarjetasPrincipales() {
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
    const path = window.location.pathname;
    const urlParams = new URLSearchParams(window.location.search);

    const inputPresupuesto = document.getElementById('inputPresupuesto');
    const presupuestoActual = inputPresupuesto ? inputPresupuesto.value : '10000';

    const inputTiempoMax = document.getElementById('inputTiempoMaxDiario');
    const tiempoMaxActual = inputTiempoMax ? inputTiempoMax.value : '8';

    const parametros = new URLSearchParams();

    for (const [key, value] of urlParams.entries()) {
        if (key !== 'nombre' && key !== 'presupuesto' && key !== 'tiempo_max_diario') {
            parametros.append(key, value);
        }
    }

    parametros.set('nombre', nombreLugar);
    parametros.set('presupuesto', presupuestoActual || '10000');
    parametros.set('tiempo_max_diario', tiempoMaxActual || '8');

    let urlDetalle;
    if (path.startsWith('/lugares/filtro')) {
        urlDetalle = `/lugares/filtro/detalle?${parametros.toString()}`;
    } else {
        urlDetalle = `/lugares/detalle?${parametros.toString()}`;
    }

    console.log("Redirigiendo a:", urlDetalle);
    window.location.href = urlDetalle;
}

function formatearTiempoMinutos(minutos) {
    if (minutos < 60) {
        return `${minutos.toFixed(1)} min`;
    } else {
        const horas = Math.floor(minutos / 60);
        const minsRestantes = Math.round(minutos % 60);
        if (minsRestantes === 0) {
            return `${horas} hr${horas > 1 ? 's' : ''}`;
        } else {
            return `${horas} hr${horas > 1 ? 's' : ''} ${minsRestantes} min`;
        }
    }
}

function construirGrafoDesdeRecomendaciones(nodoPrincipal, recomendaciones) {
    const nodos = [nodoPrincipal];
    recomendaciones.forEach(r => {
        if (r.nombre && r.nombre !== nodoPrincipal) {
            nodos.push(r.nombre);
        }
    });

    const aristas = recomendaciones
        .filter(r => r.nombre && r.nombre !== nodoPrincipal)
        .map(r => {
            const tiempoTrasladoHoras = Number(r.tiempo_traslado) || 0;
            const tiempoTrasladoMinutos = tiempoTrasladoHoras * 60;
            const pesoFormateado = tiempoTrasladoMinutos > 0 ? formatearTiempoMinutos(tiempoTrasladoMinutos) : '1 min';
            return {
                origen: nodoPrincipal,
                destino: r.nombre,
                peso: pesoFormateado
            };
        });

    return { nodos, aristas };
}

function mostrarMensajeGrafo(texto, tipo = 'exito') {
    const contenedor = document.getElementById('mensaje-grafo');
    if (!contenedor) return;

    contenedor.style.display = 'block';
    contenedor.textContent = texto;

    if (tipo === 'exito') {
        contenedor.style.backgroundColor = '#d4edda';
        contenedor.style.color = '#155724';
        contenedor.style.border = '1px solid #c3e6cb';
    } else if (tipo === 'error') {
        contenedor.style.backgroundColor = '#f8d7da';
        contenedor.style.color = '#721c24';
        contenedor.style.border = '1px solid #f5c6cb';
    } else {
        contenedor.style.backgroundColor = '#fff3cd';
        contenedor.style.color = '#856404';
        contenedor.style.border = '1px solid #ffeeba';
    }

    // Opcional: ocultar el mensaje después de 4 segundos
    setTimeout(() => {
        contenedor.style.display = 'none';
    }, 4000);
}

function enviarGrafoAlBackend(grafo, idGrafo) {
    // Convertir los pesos a números (por ejemplo, 2.3 en lugar de '2.3 min')
    const aristasConvertidas = grafo.aristas.map(a => {
        const pesoNumerico = parseFloat(a.peso); // ignora " min"
        return {
            origen: a.origen,
            destino: a.destino,
            peso: isNaN(pesoNumerico) ? 1 : pesoNumerico // valor por defecto 1 si falla
        };
    });

    fetch('/api/generar_grafo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: idGrafo,
            nodos: grafo.nodos,
            aristas: aristasConvertidas
        })
    })
    .then(response => {
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log('Grafo guardado:', data.rutaArchivo);
    })    
    .catch(err => {
        console.error('Error fetch:', err);
    });
}
function generarEstrellas(puntaje) {
    const maxEstrellas = 5;
    const estrellasCompletas = Math.floor(puntaje);
    const estrellaMedia = (puntaje - estrellasCompletas) >= 0.5 ? 1 : 0;
    const estrellasVacias = maxEstrellas - estrellasCompletas - estrellaMedia;
  
    let html = "";
    for (let i = 0; i < estrellasCompletas; i++) {
      html += "&#9733;";  // estrella llena ★
    }
    if (estrellaMedia) {
      html += "&#x2605;"; // puedes usar estrella media o estrella llena, o algún icono para media estrella
      // O si no quieres media estrella, simplemente añade otra llena
    }
    for (let i = 0; i < estrellasVacias; i++) {
      html += "&#9734;";  // estrella vacía ☆
    }
    return html;
  }
  function generarNombreAleatorio() {
    const nombres = ["Ana", "Carlos", "Luis", "María", "Jorge", "Sofía", "Pedro", "Lucía", "Miguel", "Valeria"];
    const apellidos = ["Pérez", "Gómez", "Rodríguez", "Fernández", "López", "Martínez", "Sánchez", "Ramírez"];
    const nombre = nombres[Math.floor(Math.random() * nombres.length)];
    const apellido = apellidos[Math.floor(Math.random() * apellidos.length)];
    return `${nombre} ${apellido}`;
  }  
  
  async function cargarCalificaciones(idLugar) {
    const contenedor = document.getElementById('lista-comentarios');
    contenedor.innerHTML = "<p>Cargando calificaciones...</p>";
  
    try {
      const response = await fetch(`/api/calificaciones/${idLugar}`);
      if (!response.ok) throw new Error('Error al cargar calificaciones');
  
      const data = await response.json();
      const calificaciones = data.calificaciones;
      const promedio = data.promedio;
  
      if (calificaciones.length === 0) {
        contenedor.innerHTML = "<p>No hay calificaciones aún.</p>";
        return;
      }
  
      // Mostrar promedio
      contenedor.innerHTML = `<p>Promedio: ${promedio.toFixed(1)} / 5 ⭐</p>`;
  
      calificaciones.forEach(c => {
        const div = document.createElement('div');
        div.className = "comentario";
  
        const usuario = generarNombreAleatorio();
  
        div.innerHTML = `
          <strong>${usuario}</strong><br>
          <strong>Puntaje: ${generarEstrellas(c.puntaje)}</strong><br>
          <em>${c.comentario || "Sin comentario"}</em>
        `;
  
        contenedor.appendChild(div);
      });
  
    } catch (error) {
      contenedor.innerHTML = `<p>Error: ${error.message}</p>`;
    }
  }
  
  const formComentario = document.getElementById('form-comentario');
  const inputComentario = document.getElementById('input-comentario');

  formComentario.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Obtener el comentario
    const comentario = inputComentario.value.trim();
    if (!comentario) {
      alert("Por favor, escribe un comentario.");
      return;
    }

    // Obtener la calificación seleccionada (radio checked)
    const estrellas = formComentario.querySelector('input[name="star"]:checked');
    if (!estrellas) {
      alert("Por favor, selecciona una calificación.");
      return;
    }
    const puntaje = estrellas.value;

    // Aquí debes pasar el id del lugar activo; por ejemplo:
    const idLugar = obtenerIdLugarActivo(); // Define esta función según tu app

    if (!idLugar) {
      alert("ID del lugar no definido.");
      return;
    }

    try {
      const res = await fetch('/api/calificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_lugar: idLugar,
          puntaje: puntaje,
          comentario: comentario
        })
      });

      const data = await res.json();

      if (res.ok) {
        alert(data.mensaje);
        formComentario.reset();
        cargarCalificaciones(idLugar); // Recarga los comentarios para mostrar el nuevo
      } else {
        alert("Error: " + (data.error || "No se pudo enviar la calificación"));
      }
    } catch (error) {
      alert("Error al conectar con el servidor");
      console.error(error);
    }
  });

  // Ejemplo de función para obtener el id del lugar activo (ajusta según tu app)
  function obtenerIdLugarActivo() {
    // Si usas URL, o algún atributo en el DOM, o variable JS global, etc.
    return window.idLugarActual || null;
  }