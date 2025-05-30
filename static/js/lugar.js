document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('lugares')) {
        cargarLugaresDesdeAPI();
    }
});

function cargarLugaresDesdeAPI() {
    fetch('/api/lugares')
        .then(res => {
            if (!res.ok) throw new Error('Error en la respuesta de la API');
            return res.json();
        })
        .then(data => {
            const mainContenedor = document.getElementById('contenedor');
            const seccionCompletaContenedor = document.getElementById('seccion-completa');

            if (!mainContenedor || !seccionCompletaContenedor) {
                console.error("No se encontró alguno de los contenedores esperados");
                return;
            }

            mainContenedor.innerHTML = "";
            seccionCompletaContenedor.innerHTML = "";

            if (!data.lugares || data.lugares.length === 0) {
                mainContenedor.innerHTML = "<p>No hay lugares disponibles.</p>";
                return;
            }

            // Función para crear estrellas HTML según calificación
            const crearEstrellas = (calificacion) => {
                const maxEstrellas = 5;
                let estrellas = '';

                for (let i = 1; i <= maxEstrellas; i++) {
                    if (calificacion >= i) {
                        estrellas += '<span class="estrella llena">&#9733;</span>'; // estrella llena
                    } else if (calificacion >= i - 0.5) {
                        estrellas += '<span class="estrella media">&#9733;</span>'; // media estrella (puedes cambiar estilo con CSS)
                    } else {
                        estrellas += '<span class="estrella vacia">&#9734;</span>'; // estrella vacía
                    }
                }
                return estrellas;
            };

            // Crear título simple sin click
            const crearTitulo = (titulo) => {
                const h2 = document.createElement('h2');
                h2.classList.add('carrusel-titulo');
                h2.textContent = titulo;
                return h2;
            };

            // Crear carrusel con flechas y límite máximo de lugares mostrados
            const crearSeccionCarruselConTitulo = (titulo, lugares, limite = 10) => {
                const contenedor = document.createElement('div');
                contenedor.classList.add('carrusel-contenedor');

                const tituloElem = crearTitulo(titulo);
                contenedor.appendChild(tituloElem);

                const carrusel = document.createElement('div');
                carrusel.classList.add('carrusel');

                lugares.slice(0, limite).forEach(lugar => {
                    const item = document.createElement('div');
                    item.classList.add('lugar-card');

                    const precioTexto = lugar.precio === 0 ? 'Gratis' : `Desde Q ${lugar.precio}`;
                    const calificacion = lugar.calificacion || 0;
                    const estrellasHTML = crearEstrellas(calificacion);

                    item.innerHTML = `
                        <h3>${lugar.nombre}</h3>
                        <p>${lugar.direccion}</p>
                        <p>${lugar.municipio} ${lugar.departamento}</p>
                        <p>
                            <span class="calificacion-valor">${calificacion.toFixed(1)}</span>
                            <span class="estrellas">${estrellasHTML}</span>
                        </p>
                        <p>${precioTexto}</p>
                    `;

                    // Evento click para redirigir al detalle, según ruta actual
                    item.addEventListener('click', () => {
                        const path = window.location.pathname;
                        let urlDetalle;

                        if (path.startsWith('/lugares/filtro')) {
                            urlDetalle = `/lugares/filtro/detalle?nombre=${encodeURIComponent(lugar.nombre)}`;
                        } else {
                            urlDetalle = `/lugares/detalle?nombre=${encodeURIComponent(lugar.nombre)}`;
                        }

                        window.location.href = urlDetalle;
                    });

                    carrusel.appendChild(item);
                });

                // Agregar flechas de navegación solo si hay más de 5 lugares
                if (lugares.length > 5) {
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

                    contenedor.appendChild(btnIzq);
                    contenedor.appendChild(carrusel);
                    contenedor.appendChild(btnDer);
                } else {
                    contenedor.appendChild(carrusel);
                }

                return contenedor;
            };

            // Función para filtrar y añadir secciones al contenedor principal
            const filtrarYLlenarCarrusel = (titulo, filtroFn) => {
                const lugaresFiltrados = data.lugares
                    .filter(filtroFn)
                    .sort((a, b) => b.calificacion - a.calificacion);
                if (lugaresFiltrados.length) {
                    mainContenedor.appendChild(crearSeccionCarruselConTitulo(titulo, lugaresFiltrados, 10));
                }
            };

            // Aplicar filtros y crear secciones
            filtrarYLlenarCarrusel(
                "Restaurantes populares en la Capital",
                l => l.tipo.toLowerCase() === 'comida' && l.departamento.toLowerCase() === 'guatemala'
            );

            filtrarYLlenarCarrusel(
                "Lugares turísticos en Guatemala",
                l => l.tipo.toLowerCase() === 'turismo'
            );

            filtrarYLlenarCarrusel(
                "Restaurantes conocidos en el Interior",
                l => l.tipo.toLowerCase() === 'comida' && l.departamento.toLowerCase() !== 'guatemala'
            );

            filtrarYLlenarCarrusel(
                "Entretenimiento para todos",
                l => l.tipo.toLowerCase() === 'entretenimiento'
            );

            filtrarYLlenarCarrusel(
                "Lugares turísticos mejores calificados",
                l => l.tipo.toLowerCase() === 'turismo' && l.calificacion >= 4.8 && l.calificacion <= 5
            );
        })
        .catch(error => {
            console.error("Error al cargar lugares:", error);
            const mainContenedor = document.getElementById('contenedor');
            if (mainContenedor) {
                mainContenedor.innerHTML = "<p>Error al cargar lugares.</p>";
            }
        });
}
