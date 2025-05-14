import React from 'react'
import { GoogleMap, LoadScript, Marker} from '@react-google-maps/api'

const contenedor ={
    width: '100%',
    height: '50rem'
}

const centrar = {
    lat: 20.6746,
    lng: -103.44
}

function componenteMapa(){
    return(
        <LoadScript googleMapsApiKey='AIzaSyDfWSa4hkPokde5iV0kjDIn78GHwgynpTM'>
            <GoogleMap mapContainerStyle={contenedor} center={centrar} zoom={12}>
                    <Marker position={centrar}></Marker>
                </GoogleMap>
        </LoadScript>
    )
}

export default componenteMapa()
