document.addEventListener('DOMContentLoaded', () => {
    // Cargar hospedajes solo si la ruta actual incluye "hospedajes"
    if (window.location.pathname.includes('hospedajes')) {
        cargarHospedajesDesdeAPI();
    }
});

// --- Función para cargar hospedajes desde la API y mostrarlos ---
function cargarHospedajesDesdeAPI() {
    console.log("Cargando hospedajes...");

    fetch('/api/hospedajes')
        .then(res => {
            if (!res.ok) throw new Error('Error en la respuesta de la API');
            return res.json();
        })
        .then(data => {
            const lista = document.getElementById('lista-hospedajes');
            if (!lista) {
                console.warn("No se encontró el contenedor 'lista-hospedajes'");
                return;
            }

            lista.innerHTML = ""; // Limpiar lista previa

            if (!data.hospedajes || data.hospedajes.length === 0) {
                lista.innerHTML = "<li>No hay hospedajes disponibles.</li>";
                return;
            }

            data.hospedajes.forEach(hospedaje => {
                const item = document.createElement('li');
                item.innerHTML = `
                    <strong>${hospedaje.nombre}</strong><br>
                    Tipo: ${hospedaje.tipo}<br>
                    Dirección: ${hospedaje.direccion}<br>
                    Calificación: ${hospedaje.calificacion}
                `;
                lista.appendChild(item);
            });
        })
        .catch(error => {
            console.error("Error al cargar hospedajes:", error);
            const lista = document.getElementById('lista-hospedajes');
            if (lista) lista.innerHTML = '<li>Error al cargar los hospedajes.</li>';
        });
}
