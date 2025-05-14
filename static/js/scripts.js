function abrirBarra(){ //Funcion para abrir menu lateral
    document.getElementById('sidebar').style.width = '250px';
    document.getElementById('main').style.marginLeft = '250px';
}

function cerrarBarra(){ //Funcion para cerrar menu lateral
    document.getElementById('sidebar').style.width = '0';
    document.getElementById('main').style.marginLeft = '0';
}

