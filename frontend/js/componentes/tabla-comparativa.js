// Tabla producto por producto, con una columna por supermercado y el más barato resaltado.
import { crear, vaciar } from "../dom.js";
import { dinero } from "../formato.js";

export function pintarTablaComparativa(contenedor, filas, supermercados) {
  vaciar(contenedor);
  if (filas.length === 0) {
    contenedor.append(crear("p", { clase: "tabla__vacia", texto: "Ningún producto coincide con el filtro." }));
    return;
  }

  const encabezado = crear("tr", {}, [
    crear("th", { texto: "Producto", atributos: { scope: "col" } }),
    ...supermercados.map((s) => crear("th", { clase: "numero", texto: s.nombre, atributos: { scope: "col" } })),
  ]);

  const cuerpo = crear("tbody");
  for (const fila of filas) {
    const enlace = crear("a", {
      clase: "tabla__producto",
      texto: fila.producto,
      atributos: { href: `producto.html?codigo=${encodeURIComponent(fila.codigo)}` },
    });
    const minimo = Math.min(...Object.values(fila.precios));
    const celdas = supermercados.map((s) => celdaPrecio(fila, s.codigo, minimo));
    cuerpo.append(
      crear("tr", {}, [
        crear("th", { atributos: { scope: "row" } }, [enlace, crear("span", { clase: "tabla__categoria", texto: fila.categoria })]),
        ...celdas,
      ]),
    );
  }

  contenedor.append(
    crear("table", { clase: "tabla" }, [
      crear("caption", { clase: "solo-lectores", texto: "Precio de cada producto por supermercado" }),
      crear("thead", {}, [encabezado]),
      cuerpo,
    ]),
  );
}

// Se resaltan todos los supermercados empatados en el precio más bajo.
function celdaPrecio(fila, codigoSupermercado, minimo) {
  const precio = fila.precios[codigoSupermercado];
  const dudoso = fila.dudosos?.[codigoSupermercado];
  if (dudoso !== undefined) {
    return crear("td", { clase: "numero" }, [
      crear("s", { clase: "precio--dudoso", texto: dinero(dudoso) }),
      crear("span", { clase: "precio__marca", texto: "dudoso" }),
    ]);
  }
  if (precio === undefined) {
    return crear("td", { clase: "numero precio--vacio", texto: "—", atributos: { title: "No encontrado ese día" } });
  }
  const esMejor = precio === minimo;
  return crear("td", {
    clase: `numero${esMejor ? " precio--mejor" : ""}`,
    texto: dinero(precio),
    atributos: esMejor ? { title: "Precio más bajo" } : {},
  });
}
