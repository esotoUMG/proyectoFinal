document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('hospedajes')) {
        cargarHospedajesDesdeAPI();
    }
});

function cargarHospedajesDesdeAPI() {
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

            contenedor.innerHTML = "";

            if (!data.hospedajes || data.hospedajes.length === 0) {
                contenedor.innerHTML = "<p>No hay hospedajes disponibles.</p>";
                return;
            }

            const crearCarrusel = (hospedajesArray, titulo) => {
                const seccion = document.createElement('div');
                seccion.classList.add('carrusel-contenedor');

                // Agregamos solo el título sin clickeable
                const h2 = document.createElement('h2');
                h2.classList.add('carrusel-titulo');
                h2.textContent = titulo;
                seccion.appendChild(h2);

                const carrusel = document.createElement('div');
                carrusel.classList.add('carrusel');

                const hospedajesAMostrar = hospedajesArray.slice(0, 10);

                hospedajesAMostrar.forEach(hospedaje => {
                    const item = document.createElement('div');
                    item.classList.add('lugar-card');

                    const precio = hospedaje.precio === 0 ? "Gratis" : `Desde Q ${hospedaje.precio}`;
                    const estrellasHTML = generarEstrellasHTML(hospedaje.calificacion);

                    item.innerHTML = `
                        <h3>${hospedaje.nombre}</h3>
                        <p><strong><i>${hospedaje.tipo}</i></strong></p>
                        <p>${hospedaje.direccion}</p>
                        <p>${hospedaje.municipio} ${hospedaje.departamento}</p>
                        <p>
                            <span class="calificacion-valor">${hospedaje.calificacion.toFixed(1)}</span>
                            <span class="estrellas">${estrellasHTML}</span>
                        </p>
                        <p>${precio}</p>
                    `;

                    item.addEventListener('click', () => {
                        window.location.href = `/hospedajes/detalle?nombre=${encodeURIComponent(hospedaje.nombre)}`;
                    });

                    carrusel.appendChild(item);
                });

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

                return seccion;
            };

            const generarEstrellasHTML = (calificacion) => {
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
            };

            const filtrarYLlenarCarrusel = (titulo, filtroFn) => {
                const hospedajesFiltrados = data.hospedajes.filter(filtroFn);
                if (hospedajesFiltrados.length) {
                    contenedor.appendChild(crearCarrusel(hospedajesFiltrados, titulo));
                }
            };

            // FILTROS
            filtrarYLlenarCarrusel(
                "Hospedajes en Guatemala",
                h => h.departamento.toLowerCase() === 'guatemala' && h.tipo.toLowerCase() === 'hotel'
            );

            filtrarYLlenarCarrusel(
                "Todos los hospedajes",
                h => h.tipo.toLowerCase() === 'hotel'
            );

        })
        .catch(error => {
            console.error("Error al cargar hospedajes:", error);
            const contenedor = document.getElementById('lista-hospedajes');
            if (contenedor) contenedor.innerHTML = '<p>Error al cargar los hospedajes.</p>';
        });
}
