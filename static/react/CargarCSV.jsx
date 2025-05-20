import React, { useState } from 'react';

function CargarCSV() {
  const [archivo, setArchivo] = useState(null);
  const [mensaje, setMensaje] = useState('');

  const manejarArchivo = (e) => {
    setArchivo(e.target.files[0]);
  };

  const enviarCSV = async (tipo) => {
    if (!archivo) {
      setMensaje('Selecciona un archivo .csv');
      return;
    }

    const formData = new FormData();
    formData.append('archivo', archivo);

    const url = tipo === 'lugares' ? '/api/cargar-lugares' : '/api/cargar-calificaciones';

    try {
      const respuesta = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      const data = await respuesta.json();
      setMensaje(data.mensaje || data.error || 'Operación completada');
    } catch (error) {
      setMensaje('Error al enviar: ' + error.message);
    }
  };

  return (
    <div style={{ padding: '1rem', maxWidth: '500px' }}>
      <h3>Carga de archivos CSV</h3>
      <input type="file" accept=".csv" onChange={manejarArchivo} />
      <br /><br />
      <button onClick={() => enviarCSV('lugares')}>Cargar Lugares</button>
      <button onClick={() => enviarCSV('calificaciones')}>Cargar Calificaciones</button>
      <p>{mensaje}</p>
    </div>
  );
}

export default CargarCSV;
