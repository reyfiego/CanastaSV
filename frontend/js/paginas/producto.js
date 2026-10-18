// Página de detalle: precios de hoy por supermercado e historial de un producto.
import { obtenerHistorial, obtenerProductos, obtenerSupermercados } from "../api.js";
import { dinero, fechaLarga } from "../formato.js";
import { crear, vaciar } from "../dom.js";
import { mostrarAviso, ocultarAviso } from "../componentes/aviso.js";
import { pintarEstadisticas } from "../componentes/estadisticas.js";
import { pintarLineas } from "../componentes/grafica-lineas.js";

const $ = (id) => document.getElementById(id);

async function iniciar() {
  const codigo = new URLSearchParams(location.search).get("codigo");
  if (!codigo) {
    mostrarAviso($("aviso"), "Falta el producto.", "Entra desde el comparador de la página de inicio.");
    return;
  }

  let productos;
  let supermercados;
  let historial;
  try {
    [productos, supermercados, historial] = await Promise.all([
      obtenerProductos(),
      obtenerSupermercados(),
      obtenerHistorial(codigo),
    ]);
  } catch (error) {
    mostrarAviso($("aviso"), "No se pudo cargar el producto.", error.message);
    return;
  }

  const producto = productos.find((p) => p.codigo === codigo);
  if (!producto || historial.length === 0) {
    mostrarAviso($("aviso"), "Sin datos.", "Este producto todavía no tiene precios guardados.");
    return;
  }
  ocultarAviso($("aviso"));
  document.body.classList.add("con-datos");

  const nombres = Object.fromEntries(supermercados.map((s) => [s.codigo, s.nombre]));
  document.title = `${producto.nombre} · CanastaSV`;
  $("categoria").textContent = producto.categoria;
  $("nombre").textContent = producto.nombre;

  const ultimaFecha = historial.map((p) => p.fecha).sort().at(-1);
  const hoy = historial.filter((p) => p.fecha === ultimaFecha).sort((a, b) => a.precio - b.precio);

  pintarResumen(historial, hoy, nombres);
  pintarPreciosDeHoy(hoy, nombres, ultimaFecha);
  pintarHistorial(historial, nombres, producto.nombre);
}

function pintarResumen(historial, hoy, nombres) {
  const masBarato = hoy[0];
  const masCaro = hoy.at(-1);
  const dias = new Set(historial.map((p) => p.fecha)).size;
  pintarEstadisticas($("estadisticas"), [
    { valor: dinero(masBarato.precio), etiqueta: `Precio más bajo hoy · ${nombres[masBarato.supermercado] ?? masBarato.supermercado}` },
    { valor: dinero(masCaro.precio - masBarato.precio), etiqueta: "Diferencia entre el más caro y el más barato" },
    { valor: String(dias), etiqueta: dias === 1 ? "Día con datos" : "Días con datos" },
  ]);
}

function pintarPreciosDeHoy(hoy, nombres, fecha) {
  const lista = $("precios-hoy");
  vaciar(lista);
  hoy.forEach((punto, indice) => {
    const precio = crear("strong", { texto: dinero(punto.precio) });
    if (indice === 0) precio.classList.add("precio--mejor");
    const enlace = crear("a", {
      texto: punto.nombre_en_tienda,
      atributos: { href: punto.url, target: "_blank", rel: "noopener noreferrer" },
    });
    lista.append(
      crear("li", { clase: "lista-filas__fila" }, [
        crear("span", {}, [crear("strong", { texto: nombres[punto.supermercado] ?? punto.supermercado }), crear("br"), enlace]),
        precio,
      ]),
    );
  });
  $("fecha-precios").textContent = `Precios del ${fechaLarga(fecha)}. Toca un producto para verlo en la tienda.`;
}

function pintarHistorial(historial, nombres, nombreProducto) {
  const porSupermercado = new Map();
  for (const punto of historial) {
    if (!porSupermercado.has(punto.supermercado)) porSupermercado.set(punto.supermercado, []);
    porSupermercado.get(punto.supermercado).push({ fecha: punto.fecha, precio: punto.precio });
  }
  const series = [...porSupermercado].map(([codigo, puntos]) => ({ nombre: nombres[codigo] ?? codigo, puntos }));
  pintarLineas($("grafica-historial"), $("leyenda-historial"), series, `Historial de precios de ${nombreProducto} por supermercado`);
}

iniciar();
