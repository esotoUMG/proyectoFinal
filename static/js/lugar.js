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

            // Crear título clickeable, recibe filtroParametros para armar URL solo con lo que quieres
            const crearTituloClickeable = (titulo, lugaresTipo, filtroParametros = {}) => {
                const h2 = document.createElement('h2');
                h2.classList.add('carrusel-titulo');
                h2.textContent = titulo;

                if (lugaresTipo.length > 7) {
                    h2.classList.add('clickeable');
                    h2.title = "Ver todos";
                    h2.style.cursor = "pointer";
                    h2.addEventListener('click', () => {
                        const params = new URLSearchParams();

                        if (filtroParametros.tipo) {
                            params.append('tipo', filtroParametros.tipo);
                        }
                        if (filtroParametros.departamento) {
                            params.append('departamento', filtroParametros.departamento);
                        }
                        if (filtroParametros.calificacion_min !== undefined) {
                            params.append('calificacion_min', filtroParametros.calificacion_min);
                        }
                        if (filtroParametros.calificacion_max !== undefined) {
                            params.append('calificacion_max', filtroParametros.calificacion_max);
                        }

                        const queryString = params.toString();
                        const url = queryString ? `/lugares/filtro?${queryString}` : `/lugares/filtro`;
                        window.location.href = url;
                    });
                }
                return h2;
            };

            // Crear carrusel con flechas
            const crearSeccionCarruselConTitulo = (titulo, lugares, limite = 7, filtroParametros = {}) => {
                const contenedor = document.createElement('div');
                contenedor.classList.add('carrusel-contenedor');
            
                const tituloElem = crearTituloClickeable(titulo, lugares, filtroParametros);
                contenedor.appendChild(tituloElem);
            
                const carrusel = document.createElement('div');
                carrusel.classList.add('carrusel');
            
                lugares.slice(0, limite).forEach(lugar => {
                    const item = document.createElement('div');
                    item.classList.add('lugar-card');
            
                    // Precio con validación
                    const precioTexto = lugar.precio === 0 ? 'Gratis' : `Desde Q ${lugar.precio}`;
            
                    // Crear estrellas para la calificación
                    const calificacion = lugar.calificacion;
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
            
                    // Agregar listener para redirigir a detalle al click
                    item.addEventListener('click', () => {
                        window.location.href = `/lugares/detalle?nombre=${encodeURIComponent(lugar.nombre)}`;
                    });
            
                    carrusel.appendChild(item);
                });
            
                // Solo agregar flechas si hay más de 5 lugares
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
                    // Si no hay más de 5, solo se muestra el carrusel sin flechas
                    contenedor.appendChild(carrusel);
                }
            
                return contenedor;
            };
            
            // Función para crear estrellas llenas, medias o vacías según la calificación
            const crearEstrellas = (calificacion) => {
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
            
            // Función para filtrar y agregar carrusel, recibe filtroFn y filtroParametros para la URL
            const filtrarYLlenarCarrusel = (titulo, filtroFn, filtroParametros = {}) => {
                const lugaresFiltrados = data.lugares.filter(filtroFn)
                    .sort((a, b) => b.calificacion - a.calificacion);
                if (lugaresFiltrados.length) {
                    mainContenedor.appendChild(crearSeccionCarruselConTitulo(titulo, lugaresFiltrados, 7, filtroParametros));
                }
            };

            // FILTROS
            filtrarYLlenarCarrusel(
                "Restaurantes populares en la Capital",
                l => l.tipo === 'Comida' && l.departamento.toLowerCase() === 'guatemala',
                { tipo: 'Comida', departamento: 'Guatemala' }
            );

            filtrarYLlenarCarrusel(
                "Lugares turísticos en Guatemala",
                l => l.tipo === 'Turismo',
                { tipo: 'Turismo' }
            );

            filtrarYLlenarCarrusel(
                "Restaurantes conocidos en el Interior",
                l => l.tipo === 'Comida' && l.departamento.toLowerCase() !== 'guatemala',
                { tipo: 'Comida' }
            );

            filtrarYLlenarCarrusel(
                "Entretenimiento para todos",
                l => l.tipo === 'Entretenimiento',
                { tipo: 'Entretenimiento' }
            );

            filtrarYLlenarCarrusel(
                "Lugares turísticos mejores calificados",
                l => l.tipo === 'Turismo' && l.calificacion >= 4.8 && l.calificacion <= 5,
                { tipo: 'Turismo', calificacion_min: 4.8, calificacion_max: 5 }
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
