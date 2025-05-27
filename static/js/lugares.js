document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/lugares')
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al cargar los lugares');
        }
        return response.json();
      })
      .then(data => {
        const lista = document.getElementById('lista-lugares');
        if (!data.lugares || data.lugares.length === 0) {
          lista.innerHTML = '<li>No hay lugares disponibles.</li>';
          return;
        }

        data.lugares.forEach(lugar => {
          const item = document.createElement('li');
          item.innerHTML = `
            <strong>${lugar.nombre}</strong><br>
            Tipo: ${lugar.tipo}<br>
            Precio: Q${lugar.precio}<br>
            Calificación: ${lugar.calificacion}
          `;
          lista.appendChild(item);
        });
      })
      .catch(error => {
        console.error('Error al obtener lugares:', error);
        const lista = document.getElementById('lista-lugares');
        lista.innerHTML = '<li>Error al cargar los lugares.</li>';
      });
  });