// Página de inicio: cifras clave, comparador con filtros, costo por súper y lista óptima.
import { obtenerComparativa, obtenerSupermercados } from "../api.js";
import { fechaLarga, dinero } from "../formato.js";
import { mostrarAviso, ocultarAviso } from "../componentes/aviso.js";
import { pintarEstadisticas } from "../componentes/estadisticas.js";
import { crearFiltros, aplicarFiltros, FILTROS_INICIALES } from "../componentes/filtros.js";
import { pintarTablaComparativa } from "../componentes/tabla-comparativa.js";
import { pintarBarras } from "../componentes/grafica-barras.js";
import { pintarListaPrecios } from "../componentes/lista-precios.js";

const $ = (id) => document.getElementById(id);

async function iniciar() {
  let comparativa;
  let supermercados;
  try {
    [comparativa, supermercados] = await Promise.all([obtenerComparativa(), obtenerSupermercados()]);
  } catch (error) {
    mostrarAviso($("aviso"), "No se pudieron cargar los precios.", error.message);
    return;
  }

  if (!comparativa.fecha) {
    mostrarAviso($("aviso"), "Todavía no hay precios.", "Corre la primera recolección con: python -m canastasv recolectar");
    return;
  }
  ocultarAviso($("aviso"));
  document.body.classList.add("con-datos");

  $("fecha-actualizacion").textContent = `Precios del ${fechaLarga(comparativa.fecha)}`;
  const nombres = Object.fromEntries(supermercados.map((s) => [s.codigo, s.nombre]));
  // Solo los supermercados con precios ese día (uno desactivado no aparece como columna vacía).
  supermercados = supermercados.filter((s) => comparativa.supermercados.includes(s.codigo));
  const completas = comparativa.filas.filter((f) => supermercados.every((s) => s.codigo in f.precios));

  pintarResumen(comparativa, supermercados, completas);
  pintarComparador(comparativa.filas, supermercados);
  pintarCostoPorSupermercado(comparativa, nombres, completas.length);
  pintarListaOptima(completas, nombres, comparativa);
}

function pintarResumen(comparativa, supermercados, completas) {
  pintarEstadisticas($("estadisticas"), [
    { valor: String(comparativa.filas.length), etiqueta: "Productos con precio hoy" },
    { valor: String(supermercados.length), etiqueta: "Supermercados comparados" },
    { valor: dinero(comparativa.total_lista_optima), etiqueta: `Canasta óptima (${completas.length} productos)` },
    { valor: dinero(comparativa.ahorro_vs_mejor_supermercado), etiqueta: "Ahorro frente al súper más barato" },
  ]);
}

function pintarComparador(filas, supermercados) {
  const categorias = [...new Set(filas.map((f) => f.categoria))].sort();
  const actualizar = (filtros) => pintarTablaComparativa($("tabla"), aplicarFiltros(filas, filtros), supermercados);
  crearFiltros($("filtros"), categorias, actualizar);
  actualizar(FILTROS_INICIALES);
}

function pintarCostoPorSupermercado(comparativa, nombres, cantidadCompletas) {
  const datos = Object.entries(comparativa.total_por_supermercado).map(([codigo, total]) => ({
    etiqueta: nombres[codigo] ?? codigo,
    valor: total,
  }));
  datos.push({ etiqueta: "Lista óptima", valor: comparativa.total_lista_optima, destacado: true });
  pintarBarras($("grafica-costo"), datos, "Costo total de la canasta en cada supermercado y en la lista óptima");
  $("nota-costo").textContent =
    `Suma de los ${cantidadCompletas} productos que se encontraron en todos los supermercados, para que la comparación sea justa.`;
}

function pintarListaOptima(completas, nombres, comparativa) {
  const filas = completas.map((fila) => ({
    nombre: fila.producto,
    detalle: nombres[fila.mas_barato] ?? fila.mas_barato,
    valor: dinero(fila.precios[fila.mas_barato]),
  }));
  pintarListaPrecios($("lista-optima"), filas);
  $("total-optima").textContent = dinero(comparativa.total_lista_optima);
}

iniciar();
