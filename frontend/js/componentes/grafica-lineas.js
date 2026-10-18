// Gráfica de líneas del historial de precios, una serie por supermercado.
// series: [{ nombre, puntos: [{ fecha, precio }] }]. Se distinguen por trazo, no solo por color.
import { crear, crearSvg, vaciar } from "../dom.js";
import { dinero, fechaCorta } from "../formato.js";

const ANCHO = 800;
const ALTO = 320;
const MARGEN = { arriba: 24, abajo: 36, izquierda: 64, derecha: 16 };
const ESTILOS = [
  { color: "var(--color-terracota)", guiones: "" },
  { color: "var(--color-tinta)", guiones: "6 4" },
  { color: "var(--color-grafito)", guiones: "2 4" },
  { color: "var(--color-ceniza)", guiones: "10 4 2 4" },
];

export function pintarLineas(contenedorGrafica, contenedorLeyenda, series, descripcion) {
  vaciar(contenedorGrafica);
  vaciar(contenedorLeyenda);

  const fechas = [...new Set(series.flatMap((s) => s.puntos.map((p) => p.fecha)))].sort();
  const precios = series.flatMap((s) => s.puntos.map((p) => p.precio));
  const [minimo, maximo] = rangoConHolgura(Math.min(...precios), Math.max(...precios));

  const anchoUtil = ANCHO - MARGEN.izquierda - MARGEN.derecha;
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo;
  const x = (fecha) =>
    fechas.length === 1
      ? MARGEN.izquierda + anchoUtil / 2
      : MARGEN.izquierda + (fechas.indexOf(fecha) / (fechas.length - 1)) * anchoUtil;
  const y = (precio) => MARGEN.arriba + (1 - (precio - minimo) / (maximo - minimo)) * altoUtil;

  const svg = crearSvg("svg", { class: "grafica", viewBox: `0 0 ${ANCHO} ${ALTO}`, role: "img", "aria-label": descripcion });
  const base = ALTO - MARGEN.abajo;
  svg.append(
    crearSvg("line", { class: "grafica__eje", x1: MARGEN.izquierda, x2: ANCHO - MARGEN.derecha, y1: base, y2: base }),
    crearSvg("line", { class: "grafica__eje", x1: MARGEN.izquierda, x2: MARGEN.izquierda, y1: MARGEN.arriba, y2: base }),
  );

  for (const valor of marcas(minimo, maximo)) {
    svg.append(crearSvg("text", { class: "grafica__texto", x: MARGEN.izquierda - 10, y: y(valor) + 4, "text-anchor": "end" }, dinero(valor)));
  }
  const fechasVisibles = fechas.length <= 8 ? fechas : [fechas[0], fechas[Math.floor(fechas.length / 2)], fechas.at(-1)];
  for (const fecha of fechasVisibles) {
    svg.append(crearSvg("text", { class: "grafica__texto", x: x(fecha), y: base + 22, "text-anchor": "middle" }, fechaCorta(fecha)));
  }

  series.forEach((serie, indice) => {
    const estilo = ESTILOS[indice % ESTILOS.length];
    const puntos = [...serie.puntos].sort((a, b) => a.fecha.localeCompare(b.fecha));
    if (puntos.length > 1) {
      svg.append(
        crearSvg("polyline", {
          class: "grafica__linea",
          points: puntos.map((p) => `${x(p.fecha)},${y(p.precio)}`).join(" "),
          style: `stroke: ${estilo.color}`,
          "stroke-dasharray": estilo.guiones,
        }),
      );
    }
    for (const punto of puntos) {
      const circulo = crearSvg("circle", { cx: x(punto.fecha), cy: y(punto.precio), r: 4, style: `fill: ${estilo.color}` });
      circulo.append(crearSvg("title", {}, `${serie.nombre}: ${dinero(punto.precio)} (${fechaCorta(punto.fecha)})`));
      svg.append(circulo);
    }
    contenedorLeyenda.append(itemLeyenda(serie.nombre, estilo));
  });

  contenedorGrafica.append(svg);
}

function itemLeyenda(nombre, estilo) {
  const muestra = crearSvg("svg", { width: 28, height: 8, "aria-hidden": "true" });
  muestra.append(crearSvg("line", { x1: 0, x2: 28, y1: 4, y2: 4, style: `stroke: ${estilo.color}`, "stroke-width": 3, "stroke-dasharray": estilo.guiones }));
  return crear("span", { clase: "leyenda__item" }, [muestra, document.createTextNode(nombre)]);
}

function rangoConHolgura(minimo, maximo) {
  const margen = Math.max((maximo - minimo) * 0.15, maximo * 0.05, 0.05);
  return [Math.max(0, minimo - margen), maximo + margen];
}

function marcas(minimo, maximo, cantidad = 4) {
  const paso = (maximo - minimo) / cantidad;
  return Array.from({ length: cantidad + 1 }, (_, i) => minimo + paso * i);
}
