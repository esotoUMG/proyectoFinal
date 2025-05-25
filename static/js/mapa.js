document.addEventListener('DOMContentLoaded', function () {
    // Coordenadas por defecto (Ciudad de Guatemala)
    const defaultCoords = [14.64072, -90.51327];
    
    // Inicializar mapa con las coords por defecto
    const mapa = L.map('contenedor__mapa').setView(defaultCoords, 16);
  
    // Cargar tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapa);
  
    // Función para poner marcador y centrar mapa
    function setMarker(coords, text) {
      mapa.setView(coords, 16); // zoom más cercano
      L.marker(coords)
        .addTo(mapa)
        .bindPopup(text)
        .openPopup();
    }
  
    // Intentar obtener ubicación actual
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userCoords = [position.coords.latitude, position.coords.longitude];
          setMarker(userCoords, 'Tu ubicación');
        },
        (error) => {
          // Si error o permiso denegado, usar ubicación por defecto
          setMarker(defaultCoords, 'Guatemala, Guatemala (ubicación por defecto)');
        }
      );
    } else {
      // Si el navegador no soporta geolocalización
      setMarker(defaultCoords, 'Guatemala, Guatemala (ubicación por defecto)');
    }
  });
  