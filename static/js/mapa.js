document.addEventListener('DOMContentLoaded', function () {

  const defaultCoords = [14.64072, -90.51327];

  // Verificar que el contenedor existe
  const contenedorMapa = document.getElementById('contenedor__mapa');
  if (!contenedorMapa) {
    console.error("No se encontró el contenedor del mapa con id 'contenedor__mapa'");
    return;
  }

  // Inicializar el mapa
  const mapa = L.map(contenedorMapa).setView(defaultCoords, 16);

  // Agregar capa de tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(mapa);

  // Función para poner marcador y centrar mapa
  function setMarker(coords, text) {
    mapa.setView(coords, 16);
    L.marker(coords)
      .addTo(mapa)
      .bindPopup(text)
      .openPopup();
  }

  // Intentar usar geolocalización
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userCoords = [position.coords.latitude, position.coords.longitude];
        setMarker(userCoords, 'Tu ubicación');
      },
      (error) => {
        console.warn("No se pudo obtener ubicación, usando coordenadas por defecto");
        setMarker(defaultCoords, 'Guatemala, Guatemala (ubicación por defecto)');
      }
    );
  } else {
    console.warn("Geolocalización no soportada por el navegador");
    setMarker(defaultCoords, 'Guatemala, Guatemala (ubicación por defecto)');
  }
});
