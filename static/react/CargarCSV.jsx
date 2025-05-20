import React, { useState } from 'react';

export default function CargarCSV() {
  const [archivo, setArchivo] = useState(null);
  const [tipoCarga, setTipoCarga] = useState('lugares');
  const [mensaje, setMensaje] = useState('');

  const manejarCambioArchivo = (e) => {
    setArchivo(e.target.files[0]);
  };

  const manejarCambioTipo = (e) => {
    setTipoCarga(e.target.value);
  };

  const enviarArchivo = async () => {
    if (!archivo) {
      setMensaje('Selecciona un archivo .csv para cargar.');
      return;
    }

    const formData = new FormData();
    formData.append('archivo', archivo);

    try {
      const respuesta = await fetch(`/api/cargar-${tipoCarga}`, {
        method: 'POST',
        body: formData,
      });

      const data = await respuesta.json();
      setMensaje(data.mensaje || data.error || 'Respuesta recibida.');
    } catch (error) {
      setMensaje('Error de red: ' + error.message);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white shadow-2xl rounded-2xl">
      <h2 className="text-xl font-bold mb-4 text-center">Carga Masiva de Datos CSV</h2>

      <label className="block mb-2 font-semibold">Selecciona el tipo de carga:</label>
      <select
        value={tipoCarga}
        onChange={manejarCambioTipo}
        className="w-full p-2 border rounded mb-4"
      >
        <option value="lugares">Lugares (turísticos y hospedajes)</option>
        <option value="calificaciones">Calificaciones de usuarios</option>
      </select>

      <input
        type="file"
        accept=".csv"
        onChange={manejarCambioArchivo}
        className="w-full p-2 border rounded mb-4"
      />

      <button
        onClick={enviarArchivo}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
      >
        Subir CSV
      </button>

      {mensaje && <p className="mt-4 text-center text-sm text-gray-700">{mensaje}</p>}
    </div>
  );
}
