function initMap() {
  const urlParams = new URLSearchParams(window.location.search);
  const nombreLugar = urlParams.get('nombre');
  if (!nombreLugar) return console.error("No se proporcionó un nombre en la URL");

  const defaultCoords = { lat: 17.2216, lng: -89.6236 };
  const contenedorMapa = document.getElementById('contenedor__mapa');
  if (!contenedorMapa) return console.error("No se encontró el contenedor del mapa");

  const mapa = new google.maps.Map(contenedorMapa, {
    center: defaultCoords,
    zoom: 13
  });

  let lugarPrincipalCoords = null;
  let directionsService = new google.maps.DirectionsService();
  let directionsRenderer = new google.maps.DirectionsRenderer({ suppressMarkers: true });
  directionsRenderer.setMap(mapa);

  // Variable para controlar el infoWindow abierto actualmente (solo 1 a la vez)
  let currentInfoWindow = null;

  // Función para crear un infoWindow sin botón cerrar (sin "x")
  function createInfoWindowSinCerrar(content) {
    // Crear un InfoWindow con la opción disableAutoPan para que no cierre al hacer click fuera
    const infowindow = new google.maps.InfoWindow({
      content,
      // Ojo, la API no tiene opción oficial para quitar la "x" pero podemos ocultarla con CSS:
      // Agrega un id o clase al contenido para aplicar estilo
    });
    return infowindow;
  }

  function addMarker(coords, titulo, onClick, mostrarInfoInmediata = false, esLugarPrincipal = false) {
    const marker = new google.maps.Marker({
      position: coords,
      map: mapa,
      title: titulo
    });

    // Crear contenido del infoWindow
    const contentString = `<div><b>${titulo}</b></div>`;

    // Crear infoWindow, distinto para lugar principal y para recomendaciones
    let infowindow;
    if (esLugarPrincipal) {
      infowindow = createInfoWindowSinCerrar(contentString);
    } else {
      infowindow = new google.maps.InfoWindow({
        content: contentString
      });
    }

    // Listener para toggle infoWindow en marcadores de recomendación
    marker.addListener("click", () => {
      if (esLugarPrincipal) {
        // Lugar principal: infoWindow siempre abierto, no cerrar ni toggle
        if (!infowindow.getMap()) {
          infowindow.open(mapa, marker);
        }
        return;
      }

      // Si ya hay un infoWindow abierto y es este mismo, cerrarlo (toggle)
      if (currentInfoWindow === infowindow) {
        infowindow.close();
        currentInfoWindow = null;
      } else {
        // Si hay otro infoWindow abierto, cerrar primero
        if (currentInfoWindow) currentInfoWindow.close();

        // Abrir este infoWindow y asignarlo como actual
        infowindow.open(mapa, marker);
        currentInfoWindow = infowindow;

        // Ejecutar función adicional si existe
        if (onClick) onClick(coords);
      }
    });

    // Mostrar infoWindow del lugar principal inmediatamente sin botón cerrar
    if (mostrarInfoInmediata && esLugarPrincipal) {
      infowindow.open(mapa, marker);
      currentInfoWindow = infowindow; // Para evitar cerrar con otros clicks
      // También ocultamos la 'x' con CSS abajo
    }

    return marker;
  }

  function trazarRuta(destinoCoords) {
    if (!lugarPrincipalCoords) return;

    const request = {
      origin: lugarPrincipalCoords,
      destination: destinoCoords,
      travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, (result, status) => {
      if (status === 'OK') {
        directionsRenderer.setDirections(result);
      } else {
        console.error('Error al trazar ruta:', status);
      }
    });
  }

  // Ubicación del usuario
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userCoords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        addMarker(userCoords, "Tu ubicación");
      },
      () => {
        console.warn("No se pudo obtener la ubicación del usuario.");
      }
    );
  }

  // Lugar principal
  fetch(`/api/lugar?nombre=${encodeURIComponent(nombreLugar)}`)
    .then(res => res.json())
    .then(data => {
      if (data.lugar) {
        const lat = parseFloat(data.lugar.latitud);
        const lng = parseFloat(data.lugar.longitud);
        if (!isNaN(lat) && !isNaN(lng)) {
          lugarPrincipalCoords = { lat, lng };
          mapa.setCenter(lugarPrincipalCoords);
          mapa.setZoom(15);

          addMarker(
            lugarPrincipalCoords,
            data.lugar.nombre,
            null,
            true, // Mostrar info inmediatamente
            true  // Es lugar principal (infoWindow siempre visible y sin "x")
          ).setAnimation(google.maps.Animation.DROP);
        }
      }
    });

  // Recomendaciones
  fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombreLugar)}`)
    .then(res => res.json())
    .then(data => {
      if (data.recomendaciones) {
        data.recomendaciones.forEach(lugar => {
          const lat = parseFloat(lugar.latitud);
          const lng = parseFloat(lugar.longitud);
          if (!isNaN(lat) && !isNaN(lng)) {
            addMarker(
              { lat, lng },
              lugar.nombre,
              (coords) => trazarRuta(coords)
            );
          }
        });
      }
    });
}
