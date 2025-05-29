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

            const crearTituloClickeable = (titulo, itemsTipo, filtroParametros = {}) => {
                const h2 = document.createElement('h2');
                h2.classList.add('carrusel-titulo');
                h2.textContent = titulo;

                if (itemsTipo.length > 7) {
                    h2.classList.add('clickeable');
                    h2.title = "Ver todos";
                    h2.style.cursor = "pointer";
                    h2.addEventListener('click', () => {
                        const params = new URLSearchParams();

                        // tipo es obligatorio para el backend
                        if (filtroParametros.tipo) {
                            params.append('tipo', filtroParametros.tipo.toLowerCase());
                        } else {
                            // Por defecto usaremos 'hotel' como tipo general
                            params.append('tipo', 'hotel');
                        }

                        if (filtroParametros.departamento) {
                            params.append('departamento', filtroParametros.departamento.toLowerCase());
                        }

                        const url = `/hospedajes/filtro?${params.toString()}`;
                        console.log("Redirigiendo a:", url);  // para debug
                        window.location.href = url;
                    });
                }

                return h2;
            };

            const crearCarrusel = (hospedajesArray, titulo, filtroParametros = {}) => {
                const seccion = document.createElement('div');
                seccion.classList.add('carrusel-contenedor');

                const h2 = crearTituloClickeable(titulo, hospedajesArray, filtroParametros);
                seccion.appendChild(h2);

                const carrusel = document.createElement('div');
                carrusel.classList.add('carrusel');

                const hospedajesAMostrar = hospedajesArray.slice(0, 7);

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

            const filtrarYLlenarCarrusel = (titulo, filtroFn, filtroParametros = {}) => {
                const hospedajesFiltrados = data.hospedajes.filter(filtroFn);
                if (hospedajesFiltrados.length) {
                    contenedor.appendChild(crearCarrusel(hospedajesFiltrados, titulo, filtroParametros));
                }
            };

            // FILTROS
            filtrarYLlenarCarrusel(
                "Hospedajes en Guatemala",
                h => h.departamento.toLowerCase() === 'guatemala' && h.tipo.toLowerCase() === 'hotel',
                { tipo: 'hotel', departamento: 'Guatemala' }
            );

            filtrarYLlenarCarrusel(
                "Todos los hospedajes",
                h => h.tipo.toLowerCase() === 'hotel',  // también filtramos por tipo aquí
                { tipo: 'hotel' }
            );

        })
        .catch(error => {
            console.error("Error al cargar hospedajes:", error);
            const contenedor = document.getElementById('lista-hospedajes');
            if (contenedor) contenedor.innerHTML = '<p>Error al cargar los hospedajes.</p>';
        });
}
