function initMap() {
  const urlParams = new URLSearchParams(window.location.search);
  const nombreLugar = urlParams.get('nombre');
  if (!nombreLugar) return console.error("No se proporcionó un nombre en la URL");

  const defaultCoords = { lat: 17.2216, lng: -89.6236 };
  const contenedorMapa = document.getElementById('contenedor__mapa');
  if (!contenedorMapa) return console.error("No se encontró el contenedor del mapa");

  const mapa = new google.maps.Map(contenedorMapa, {
    center: defaultCoords,
    zoom: 9
  });

  let lugarPrincipalCoords = null;
  let infoWindowPrincipal = null;
  let directionsService = new google.maps.DirectionsService();
  let directionsRenderer = new google.maps.DirectionsRenderer({ suppressMarkers: true });
  directionsRenderer.setMap(mapa);

  let currentInfoWindow = null;

  // Marcadores recomendados (nombre -> marcador e infowindow)
  const marcadoresRecomendados = new Map();

  function addMarker(coords, titulo, esLugarPrincipal = false) {
    const marker = new google.maps.Marker({
      position: coords,
      map: mapa,
      title: titulo
    });

    const infowindow = new google.maps.InfoWindow({
      content: `<div><b>${titulo}</b></div>`
    });

    if (esLugarPrincipal) {
      infowindow.open(mapa, marker);
      currentInfoWindow = infowindow;
      infoWindowPrincipal = infowindow;
    }

    marker.addListener("click", () => {
      if (currentInfoWindow && currentInfoWindow !== infoWindowPrincipal) {
        currentInfoWindow.close();
      }
      infowindow.open(mapa, marker);
      currentInfoWindow = infowindow;
    });

    return { marker, infowindow };
  }

  function trazarRuta(destinoCoords, destinoMarker, destinoInfoWindow) {
    if (!lugarPrincipalCoords) return;

    const request = {
      origin: lugarPrincipalCoords,
      destination: destinoCoords,
      travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, (result, status) => {
      if (status === 'OK') {
        directionsRenderer.setDirections(result);

        if (currentInfoWindow && currentInfoWindow !== infoWindowPrincipal) {
          currentInfoWindow.close();
        }

        destinoInfoWindow.open(mapa, destinoMarker);
        currentInfoWindow = destinoInfoWindow;

        if (infoWindowPrincipal) {
          infoWindowPrincipal.open(mapa);
        }
      } else {
        console.error('Error al trazar ruta:', status);
      }
    });
  }

  // Opcional: mostrar ubicación actual del usuario con marcador especial
  function mostrarUbicacionActual() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(pos => {
        const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        new google.maps.Marker({
          position: coords,
          map: mapa,
          title: "Tu ubicación",
          icon: 'icono-usuario.png' // Cambia o elimina si quieres
        });
      }, err => {
        console.warn("Error obteniendo ubicación:", err);
      });
    }
  }

  // Primero: cargar lugar principal
  fetch(`/api/lugar?nombre=${encodeURIComponent(nombreLugar)}`)
    .then(res => res.json())
    .then(data => {
      if (!data.lugar) throw new Error("Lugar principal no encontrado");

      const lat = parseFloat(data.lugar.latitud);
      const lng = parseFloat(data.lugar.longitud);

      if (isNaN(lat) || isNaN(lng)) throw new Error("Coordenadas inválidas del lugar principal");

      lugarPrincipalCoords = { lat, lng };
      mapa.setCenter(lugarPrincipalCoords);
      mapa.setZoom(15);

      addMarker(lugarPrincipalCoords, data.lugar.nombre, true);

      // Ahora sí: cargar recomendaciones
      return Promise.all([
        fetch(`/api/recomendaciones?nombre=${encodeURIComponent(nombreLugar)}`).then(r => r.json()),
        fetch(`/api/recomendaciones_hospedajes?nombre=${encodeURIComponent(nombreLugar)}`).then(r => r.json())
      ]);
    })
    .then(([recomendacionesLugares, recomendacionesHospedajes]) => {
      if (recomendacionesLugares.recomendaciones) {
        recomendacionesLugares.recomendaciones.forEach(lugar => {
          const lat = parseFloat(lugar.latitud);
          const lng = parseFloat(lugar.longitud);
          if (!isNaN(lat) && !isNaN(lng)) {
            const coords = { lat, lng };
            const { marker, infowindow } = addMarker(coords, lugar.nombre);
            marcadoresRecomendados.set(lugar.nombre, { coords, marker, infowindow });
          }
        });
      }

      if (recomendacionesHospedajes.recomendaciones) {
        recomendacionesHospedajes.recomendaciones.forEach(hospedaje => {
          const lat = parseFloat(hospedaje.latitud);
          const lng = parseFloat(hospedaje.longitud);
          if (!isNaN(lat) && !isNaN(lng)) {
            const coords = { lat, lng };
            const { marker, infowindow } = addMarker(coords, hospedaje.nombre);
            marcadoresRecomendados.set(hospedaje.nombre, { coords, marker, infowindow });
          }
        });
      }

      mostrarUbicacionActual();
    })
    .catch(err => {
      console.error('Error inicializando mapa:', err);
    });

  // Función expuesta para que el frontend pueda trazar ruta al lugar recomendado
  window.seleccionarLugarRecomendado = function(nombreLugarSeleccionado) {
    const destino = marcadoresRecomendados.get(nombreLugarSeleccionado);
    if (destino && lugarPrincipalCoords) {
      trazarRuta(destino.coords, destino.marker, destino.infowindow);
    } else {
      console.warn('Lugar seleccionado no encontrado o lugar principal no cargado');
    }
  };
}
