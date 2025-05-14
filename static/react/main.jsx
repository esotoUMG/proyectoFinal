import React from 'react'
import ReactDOM from 'react-dom/client'
import ComponenteMapa from './mapa'
import '../css/app.css'

const ruta = ReactDOM.createRoot(document.getElementById('contenedor__mapa'))
ruta.render(
    <React.StrictMode>
        <ComponenteMapa />
    </React.StrictMode>
)
