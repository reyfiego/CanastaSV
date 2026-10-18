// Lista de filas "nombre — detalle" (lista óptima y precios de un producto por súper).
import { crear, vaciar } from "../dom.js";

// filas: [{ nombre, detalle, valor, destacado }]
export function pintarListaPrecios(contenedor, filas) {
  vaciar(contenedor);
  for (const fila of filas) {
    const valor = crear("strong", { texto: fila.valor });
    if (fila.destacado) valor.classList.add("precio--mejor");
    const detalle = crear("span", { clase: "lista-filas__detalle" }, fila.detalle ? [`${fila.detalle} · `, valor] : [valor]);
    contenedor.append(crear("li", { clase: "lista-filas__fila" }, [crear("span", { texto: fila.nombre }), detalle]));
  }
}
