// Ayudas para crear elementos sin usar innerHTML: los nombres de productos vienen de
// sitios externos, así que siempre se insertan como texto.

const SVG_NS = "http://www.w3.org/2000/svg";

export function crear(etiqueta, { clase, texto, atributos = {} } = {}, hijos = []) {
  const elemento = document.createElement(etiqueta);
  if (clase) elemento.className = clase;
  if (texto !== undefined) elemento.textContent = texto;
  for (const [nombre, valor] of Object.entries(atributos)) {
    elemento.setAttribute(nombre, valor);
  }
  elemento.append(...hijos);
  return elemento;
}

export function crearSvg(etiqueta, atributos = {}, texto) {
  const elemento = document.createElementNS(SVG_NS, etiqueta);
  for (const [nombre, valor] of Object.entries(atributos)) {
    elemento.setAttribute(nombre, valor);
  }
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

export function vaciar(elemento) {
  elemento.replaceChildren();
}
