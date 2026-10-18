// Acceso a la API de CanastaSV. Toda llamada al servidor pasa por aquí.

export class ErrorDeApi extends Error {}

async function obtenerJson(ruta) {
  let respuesta;
  try {
    respuesta = await fetch(ruta, { headers: { Accept: "application/json" } });
  } catch {
    throw new ErrorDeApi("No se pudo conectar con el servidor.");
  }
  if (!respuesta.ok) {
    throw new ErrorDeApi(`El servidor respondió con el código ${respuesta.status}.`);
  }
  return respuesta.json();
}

export const obtenerComparativa = () => obtenerJson("/api/comparativa");
export const obtenerSupermercados = () => obtenerJson("/api/supermercados");
export const obtenerProductos = () => obtenerJson("/api/productos");
export const obtenerHistorial = (codigo) =>
  obtenerJson(`/api/productos/${encodeURIComponent(codigo)}/historial`);
