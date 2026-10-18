// Muestra u oculta un mensaje de estado (sin datos, error de conexión).

export function mostrarAviso(elemento, titulo, detalle) {
  elemento.replaceChildren();
  const fuerte = document.createElement("strong");
  fuerte.textContent = titulo;
  elemento.append(fuerte, document.createTextNode(` ${detalle}`));
  elemento.hidden = false;
}

export function ocultarAviso(elemento) {
  elemento.hidden = true;
}
