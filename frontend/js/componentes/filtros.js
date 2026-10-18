// Buscador por nombre y etiquetas de categoría. Avisa con alCambiar({ texto, categoria }).
import { crear, vaciar } from "../dom.js";

const TODAS = "Todas";

export function crearFiltros(contenedor, categorias, alCambiar) {
  const estado = { texto: "", categoria: TODAS };
  vaciar(contenedor);

  const etiqueta = crear("label", { clase: "solo-lectores", texto: "Buscar producto", atributos: { for: "buscador" } });
  const buscador = crear("input", {
    clase: "buscador",
    atributos: { id: "buscador", type: "search", placeholder: "Busca arroz, frijol, leche…", autocomplete: "off" },
  });
  buscador.addEventListener("input", () => {
    estado.texto = buscador.value;
    alCambiar({ ...estado });
  });

  const grupo = crear("div", { clase: "categorias", atributos: { role: "group", "aria-label": "Filtrar por categoría" } });
  const botones = [];
  [TODAS, ...categorias].forEach((nombre, indice) => {
    if (indice > 0) grupo.append(crear("span", { clase: "categorias__separador", texto: "·", atributos: { "aria-hidden": "true" } }));
    const boton = crear("button", {
      clase: "categoria",
      texto: nombre,
      atributos: { type: "button", "aria-pressed": String(nombre === TODAS) },
    });
    boton.addEventListener("click", () => {
      estado.categoria = nombre;
      botones.forEach((b) => b.setAttribute("aria-pressed", String(b === boton)));
      alCambiar({ ...estado });
    });
    botones.push(boton);
    grupo.append(boton);
  });

  contenedor.append(etiqueta, buscador, grupo);
}

export function aplicarFiltros(filas, { texto, categoria }) {
  const buscado = normalizar(texto);
  return filas.filter(
    (fila) =>
      (categoria === TODAS || fila.categoria === categoria) &&
      (!buscado || normalizar(fila.producto).includes(buscado)),
  );
}

export const FILTROS_INICIALES = { texto: "", categoria: TODAS };

function normalizar(texto) {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
}
