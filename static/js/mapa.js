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

  let currentInfoWindow = null;

  function createInfoWindowSinCerrar(content) {
    const infowindow = new google.maps.InfoWindow({
      content,
    });
    return infowindow;
  }

  function addMarker(coords, titulo, onClick, mostrarInfoInmediata = false, esLugarPrincipal = false) {
    const marker = new google.maps.Marker({
      position: coords,
      map: mapa,
      title: titulo
    });

    const contentString = `<div><b>${titulo}</b></div>`;

    let infowindow;
    if (esLugarPrincipal) {
      infowindow = createInfoWindowSinCerrar(contentString);
    } else {
      infowindow = new google.maps.InfoWindow({
        content: contentString
      });
    }

    marker.addListener("click", () => {
      if (esLugarPrincipal) {
        if (!infowindow.getMap()) {
          infowindow.open(mapa, marker);
        }
        return;
      }

      if (currentInfoWindow === infowindow) {
        infowindow.close();
        currentInfoWindow = null;
      } else {
        if (currentInfoWindow) currentInfoWindow.close();
        infowindow.open(mapa, marker);
        currentInfoWindow = infowindow;
        if (onClick) onClick(coords);
      }
    });

    if (mostrarInfoInmediata && esLugarPrincipal) {
      infowindow.open(mapa, marker);
      currentInfoWindow = infowindow;
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

  // Ya no solicitamos ni marcamos la ubicación del usuario aquí

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
            true,
            true
          ).setAnimation(google.maps.Animation.DROP);
        }
      }
    });

  // Recomendaciones lugar
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

  // Hospedaje principal
  fetch(`/api/hospedaje?nombre=${encodeURIComponent(nombreLugar)}`)
    .then(res => res.json())
    .then(data => {
      if (data.lugar) {
        const lat = parseFloat(data.lugar.latitud);
        const lng = parseFloat(data.lugar.longitud);
        if (!isNaN(lat) && !isNaN(lng)) {
          const hospedajePrincipalCoords = { lat, lng };
          mapa.setCenter(hospedajePrincipalCoords);
          mapa.setZoom(15);

          addMarker(
            hospedajePrincipalCoords,
            data.lugar.nombre,
            null,
            true,
            true
          ).setAnimation(google.maps.Animation.DROP);
        }
      }
    });

  // Recomendaciones hospedajes
  fetch(`/api/recomendaciones_hospedajes?nombre=${encodeURIComponent(nombreLugar)}`)
    .then(res => res.json())
    .then(data => {
      if (data.recomendaciones) {
        data.recomendaciones.forEach(hospedaje => {
          const lat = parseFloat(hospedaje.latitud);
          const lng = parseFloat(hospedaje.longitud);
          if (!isNaN(lat) && !isNaN(lng)) {
            addMarker(
              { lat, lng },
              hospedaje.nombre,
              (coords) => trazarRuta(coords)
            );
          }
        });
      }
    });
}
