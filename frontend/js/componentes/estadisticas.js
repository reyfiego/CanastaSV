// Fila de cifras clave: número grande en serif con su etiqueta debajo.
import { crear, vaciar } from "../dom.js";

export function pintarEstadisticas(contenedor, items) {
  vaciar(contenedor);
  for (const { valor, etiqueta } of items) {
    contenedor.append(
      crear("div", { clase: "estadistica" }, [
        crear("span", { clase: "estadistica__valor", texto: valor }),
        crear("span", { clase: "estadistica__etiqueta", texto: etiqueta }),
      ]),
    );
  }
}
