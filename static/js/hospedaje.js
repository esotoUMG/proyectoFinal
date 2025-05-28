document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('hospedajes')) {
        cargarHospedajesDesdeAPI();
    }
});

function cargarHospedajesDesdeAPI() {
    console.log("Cargando hospedajes...");

    fetch('/api/hospedajes')
        .then(res => {
            if (!res.ok) throw new Error('Error en la respuesta de la API');
            return res.json();
        })
        .then(data => {
            const contenedor = document.getElementById('lista-hospedajes');
            if (!contenedor) {
                console.warn("No se encontró el contenedor 'lista-hospedajes'");
                return;
            }

            contenedor.innerHTML = ""; // Limpiar contenido anterior

            if (!data.hospedajes || data.hospedajes.length === 0) {
                contenedor.innerHTML = "<p>No hay hospedajes disponibles.</p>";
                return;
            }

            const hospedajesFiltrados = data.hospedajes
                .filter(h => h.calificacion >= 4.7 && h.calificacion <= 5)
                .sort((a, b) => b.calificacion - a.calificacion);

            if (hospedajesFiltrados.length === 0) {
                contenedor.innerHTML = "<p>No hay hospedajes con calificación alta (4.7 a 5).</p>";
                return;
            }

            const seccion = document.createElement('div');
            seccion.classList.add('carrusel-contenedor');

            const h2 = document.createElement('h2');
            h2.classList.add('carrusel-titulo');
            h2.textContent = "Hospedajes mejor calificados";

            if (hospedajesFiltrados.length > 7) {
                h2.classList.add('clickeable');
                h2.title = "Ver todos";
                h2.style.cursor = "pointer";
                h2.addEventListener('click', () => {
                    const params = new URLSearchParams({
                        tipo: 'Hospedaje',
                        calificacion_min: 4.7,
                        calificacion_max: 5
                    });
                    window.location.href = `/hospedajes/filtro?${params.toString()}`;
                });
            }

            seccion.appendChild(h2);

            const carrusel = document.createElement('div');
            carrusel.classList.add('carrusel');

            const hospedajesAMostrar = hospedajesFiltrados.slice(0, 7);

            hospedajesAMostrar.forEach(hospedaje => {
                const item = document.createElement('div');
                item.classList.add('lugar-card');
                item.innerHTML = `
                    <h3>${hospedaje.nombre}</h3>
                    <p>Tipo: ${hospedaje.tipo}</p>
                    <p>Dirección: ${hospedaje.direccion}</p>
                    <p>Ubicación: ${hospedaje.municipio} ${hospedaje.departamento}</p>
                    <p>Calificación: ${hospedaje.calificacion}</p>
                `;
                carrusel.appendChild(item);
            });

            // Mostrar flechas solo si hay más de 5 elementos
            if (hospedajesAMostrar.length > 5) {
                const btnIzq = document.createElement('button');
                btnIzq.classList.add('flecha', 'izquierda');
                btnIzq.setAttribute('aria-label', 'Anterior');
                btnIzq.innerHTML = '&#8592;';
                btnIzq.addEventListener('click', () => {
                    carrusel.scrollBy({ left: -250, behavior: 'smooth' });
                });

                const btnDer = document.createElement('button');
                btnDer.classList.add('flecha', 'derecha');
                btnDer.setAttribute('aria-label', 'Siguiente');
                btnDer.innerHTML = '&#8594;';
                btnDer.addEventListener('click', () => {
                    carrusel.scrollBy({ left: 250, behavior: 'smooth' });
                });

                seccion.appendChild(btnIzq);
                seccion.appendChild(carrusel);
                seccion.appendChild(btnDer);
            } else {
                seccion.appendChild(carrusel);
            }

            contenedor.appendChild(seccion);
        })
        .catch(error => {
            console.error("Error al cargar hospedajes:", error);
            const contenedor = document.getElementById('lista-hospedajes');
            if (contenedor) contenedor.innerHTML = '<p>Error al cargar los hospedajes.</p>';
        });
}
