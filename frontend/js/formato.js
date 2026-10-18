// Formato de dinero y fechas para mostrar en pantalla.

const formatoDinero = new Intl.NumberFormat("es-SV", { style: "currency", currency: "USD" });
const formatoFechaLarga = new Intl.DateTimeFormat("es-SV", { day: "numeric", month: "long", year: "numeric" });
const formatoFechaCorta = new Intl.DateTimeFormat("es-SV", { day: "numeric", month: "short" });

// Las fechas de la API vienen como "2026-10-18"; se leen como fecha local para no correr un día.
function aFecha(iso) {
  const [anio, mes, dia] = iso.split("-").map(Number);
  return new Date(anio, mes - 1, dia);
}

export const dinero = (valor) => formatoDinero.format(valor);
export const fechaLarga = (iso) => formatoFechaLarga.format(aFecha(iso));
export const fechaCorta = (iso) => formatoFechaCorta.format(aFecha(iso));

export function porcentaje(valor) {
  const signo = valor > 0 ? "+" : "";
  return `${signo}${valor.toFixed(1)} %`;
}
