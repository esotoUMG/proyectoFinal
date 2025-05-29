document.addEventListener('DOMContentLoaded', () => {
    // Variables globales dentro del DOMContentLoaded
    const formulario = document.getElementById('form-lugar');
    const mensajeDiv = document.getElementById('mensaje');
  
    // Botones si existen
    const btnLugar = document.getElementById('opcion-lugar');
    if (btnLugar) btnLugar.addEventListener('click', () => {
      window.location.href = urlCargarLugar;
    });
  
    const btnHospedaje = document.getElementById('opcion-hospedaje');
    if (btnHospedaje) btnHospedaje.addEventListener('click', () => {
      window.location.href = urlCargarHospedaje;
    });
  
    // Lista de departamentos
    const departamentos = [
      "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula",
      "El Progreso", "Escuintla", "Guatemala", "Huehuetenango",
      "Izabal", "Jalapa", "Jutiapa", "Petén", "Quetzaltenango",
      "Quiché", "Retalhuleu", "Sacatepéquez", "San Marcos",
      "Santa Rosa", "Sololá", "Suchitepéquez", "Totonicapán", "Zacapa"
    ];
  
    const selectDepartamento = document.getElementById('departamento');
    departamentos.forEach(dep => {
      const option = document.createElement('option');
      option.value = dep;
      option.textContent = dep;
      selectDepartamento.appendChild(option);
    });
  
    // Manejo del submit del formulario
    if (formulario) {
      formulario.addEventListener('submit', (e) => {
        e.preventDefault();
  
        // Leer y limpiar valores
        const precioRaw = document.querySelector('input[name="precio"]').value.trim();
        const latRaw = document.getElementById('latitud').value.trim();
        const lngRaw = document.getElementById('longitud').value.trim();
  
        // Validar campos obligatorios
        if (
          !document.getElementById('nombre').value.trim() ||
          !document.getElementById('direccion').value.trim() ||
          !selectDepartamento.value.trim() ||
          !document.getElementById('municipio').value.trim() ||
          !formulario.tipo.value.trim()
        ) {
          mensajeDiv.textContent = '❌ Por favor completa todos los campos obligatorios.';
          mensajeDiv.style.color = 'red';
          return;
        }
  
        // Parsear y validar números
        const precio = precioRaw ? parseFloat(precioRaw) : 0;
        const latitud = latRaw ? parseFloat(latRaw) : null;
        const longitud = lngRaw ? parseFloat(lngRaw) : null;
  
        if (latitud === null || longitud === null || isNaN(latitud) || isNaN(longitud)) {
          mensajeDiv.textContent = '❌ Debes indicar una ubicación válida (latitud y longitud).';
          mensajeDiv.style.color = 'red';
          return;
        }
  
        const datos = {
          nombre: document.getElementById('nombre').value.trim(),
          direccion: document.getElementById('direccion').value.trim(),
          departamento: selectDepartamento.value.trim(),
          municipio: document.getElementById('municipio').value.trim(),
          tipo: formulario.tipo.value.trim(),
          precio: precio,
          latitud: latitud,
          longitud: longitud
        };
  
        fetch('/api/registrar-lugar', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(datos)
        })
          .then(async res => {
            if (!res.ok) {
              const errorData = await res.json().catch(() => ({}));
              throw new Error(errorData.error || 'Error en la respuesta del servidor');
            }
            return res.json();
          })
          .then(respuesta => {
            if (respuesta.mensaje) {
              mensajeDiv.textContent = '✅ ' + respuesta.mensaje;
              mensajeDiv.style.color = 'green';
              formulario.reset();
              if (typeof marcador !== 'undefined' && marcador && typeof mapa !== 'undefined' && mapa) {
                marcador.setMap(null);
                marcador = null;
                initMap();
              }
            } else if (respuesta.error) {
              mensajeDiv.textContent = '❌ ' + respuesta.error;
              mensajeDiv.style.color = 'red';
            } else {
              mensajeDiv.textContent = '❌ Error desconocido al registrar el lugar.';
              mensajeDiv.style.color = 'red';
            }
          })
          .catch(err => {
            console.error('Error en fetch:', err);
            mensajeDiv.textContent = '❌ Ocurrió un error inesperado: ' + err.message;
            mensajeDiv.style.color = 'red';
          });
              fetch('/api/registrar-hospedaje', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(datos)
        })
          .then(async res => {
            if (!res.ok) {
              const errorData = await res.json().catch(() => ({}));
              throw new Error(errorData.error || 'Error en la respuesta del servidor');
            }
            return res.json();
          })
          .then(respuesta => {
            if (respuesta.mensaje) {
              mensajeDiv.textContent = '✅ ' + respuesta.mensaje;
              mensajeDiv.style.color = 'green';
              formulario.reset();
              if (typeof marcador !== 'undefined' && marcador && typeof mapa !== 'undefined' && mapa) {
                marcador.setMap(null);
                marcador = null;
                initMap();
              }
            } else if (respuesta.error) {
              mensajeDiv.textContent = '❌ ' + respuesta.error;
              mensajeDiv.style.color = 'red';
            } else {
              mensajeDiv.textContent = '❌ Error desconocido al registrar el lugar.';
              mensajeDiv.style.color = 'red';
            }
          })
          .catch(err => {
            console.error('Error en fetch:', err);
            mensajeDiv.textContent = '❌ Ocurrió un error inesperado: ' + err.message;
            mensajeDiv.style.color = 'red';
          });
      });
    }
  });
  
  
  let mapa;
  let marcador;
  let geocoder;
  
  let inputDireccion, inputDepartamento, inputMunicipio;
  let intentarGeocode;
  
  function initMap() {
    const contenedorMapa = document.getElementById('mapa');
    const inputLat = document.getElementById('latitud');
    const inputLng = document.getElementById('longitud');
    inputDireccion = document.getElementById('direccion');
    inputDepartamento = document.getElementById('departamento'); // select
    inputMunicipio = document.getElementById('municipio');
  
    geocoder = new google.maps.Geocoder();
  
    inputLat.setAttribute('readonly', true);
    inputLng.setAttribute('readonly', true);
  
    const coordsIniciales = {
      lat: parseFloat(inputLat.value) || 17.2216,
      lng: parseFloat(inputLng.value) || -89.6236,
    };
  
    mapa = new google.maps.Map(contenedorMapa, {
      center: coordsIniciales,
      zoom: 13,
    });
  
    marcador = new google.maps.Marker({
      position: coordsIniciales,
      map: mapa,
      draggable: true,
    });
  
    inputLat.value = coordsIniciales.lat;
    inputLng.value = coordsIniciales.lng;
  
    intentarGeocode = () => {
      const direccion = inputDireccion.value.trim();
      const departamento = inputDepartamento.value.trim(); // select.value
      const municipio = inputMunicipio.value.trim();
  
      if (direccion && departamento && municipio) {
        const direccionCompleta = `${direccion}, ${municipio}, ${departamento}`;
  
        geocoder.geocode({ address: direccionCompleta }, (results, status) => {
          if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
  
            inputLat.value = location.lat();
            inputLng.value = location.lng();
  
            marcador.setPosition(location);
            mapa.setCenter(location);
            mapa.setZoom(15);
          } else {
            console.warn('No se pudo geocodificar la dirección:', status);
            inputLat.value = '';
            inputLng.value = '';
          }
        });
      } else {
        inputLat.value = '';
        inputLng.value = '';
      }
    };
  
    // Eventos para inputs y select
    inputDireccion.addEventListener('input', intentarGeocode);
    inputMunicipio.addEventListener('input', intentarGeocode);
    inputDepartamento.addEventListener('change', intentarGeocode); // Select usa "change"
  
    marcador.addListener('dragend', () => {
      const pos = marcador.getPosition();
      inputLat.value = pos.lat();
      inputLng.value = pos.lng();
    });
  
    mapa.addListener('click', (e) => {
      marcador.setPosition(e.latLng);
      inputLat.value = e.latLng.lat();
      inputLng.value = e.latLng.lng();
    });
  }
  
  window.initMap = initMap;
  
  function limpiarMapa() {
    if (marcador) {
      google.maps.event.clearListeners(marcador, 'dragend');
      marcador.setMap(null);
      marcador = null;
    }
  
    if (mapa) {
      google.maps.event.clearListeners(mapa, 'click');
      mapa = null;
    }
  
    if ([inputDireccion, inputDepartamento, inputMunicipio, intentarGeocode].every(x => x)) {
      inputDireccion.removeEventListener('input', intentarGeocode);
      inputMunicipio.removeEventListener('input', intentarGeocode);
      inputDepartamento.removeEventListener('change', intentarGeocode);
    }
  
    const contenedorMapa = document.getElementById('mapa');
    if (contenedorMapa) {
      contenedorMapa.innerHTML = '';
    }
  }
  