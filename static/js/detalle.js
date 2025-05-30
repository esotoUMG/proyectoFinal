document.addEventListener("DOMContentLoaded", function () {
    const comentario = document.getElementById('input-comentario');
    const estrellas = document.querySelectorAll('input[name="star"]');
    const boton = document.getElementById('submitBtn');

function verificarFormulario() {
    const comentarioLleno = comentario.value.trim() !== "";
    const estrellaMarcada = [...estrellas].some(e => e.checked);
    boton.disabled = !(comentarioLleno && estrellaMarcada);
}

comentario.addEventListener('input', verificarFormulario);
estrellas.forEach(e => e.addEventListener('change', verificarFormulario));
});
