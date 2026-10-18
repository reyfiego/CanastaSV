// Gráfica de barras verticales en SVG. datos: [{ etiqueta, valor, destacado }].
import { crearSvg, vaciar } from "../dom.js";
import { dinero } from "../formato.js";

const ANCHO = 520;
const ALTO = 280;
const MARGEN = { arriba: 28, abajo: 40, lados: 8 };

export function pintarBarras(contenedor, datos, descripcion) {
  vaciar(contenedor);
  const svg = crearSvg("svg", {
    class: "grafica",
    viewBox: `0 0 ${ANCHO} ${ALTO}`,
    role: "img",
    "aria-label": descripcion,
  });

  const maximo = Math.max(...datos.map((d) => d.valor), 0.01);
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo;
  const anchoSlot = (ANCHO - MARGEN.lados * 2) / datos.length;
  const anchoBarra = Math.min(64, anchoSlot * 0.55);
  const base = ALTO - MARGEN.abajo;

  datos.forEach((dato, indice) => {
    const alto = (dato.valor / maximo) * altoUtil;
    const centro = MARGEN.lados + anchoSlot * indice + anchoSlot / 2;
    svg.append(
      crearSvg("rect", {
        class: `grafica__barra${dato.destacado ? " grafica__barra--destacada" : ""}`,
        x: centro - anchoBarra / 2,
        y: base - alto,
        width: anchoBarra,
        height: alto,
        rx: 2,
      }),
      crearSvg("text", { class: "grafica__valor", x: centro, y: base - alto - 8, "text-anchor": "middle" }, dinero(dato.valor)),
      crearSvg("text", { class: "grafica__texto", x: centro, y: base + 22, "text-anchor": "middle" }, dato.etiqueta),
    );
  });

  svg.append(crearSvg("line", { class: "grafica__eje", x1: 0, x2: ANCHO, y1: base, y2: base }));
  contenedor.append(svg);
}
