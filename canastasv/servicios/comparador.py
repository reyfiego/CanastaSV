"""Compara los precios de un día: más barato por producto, costo por súper y lista óptima."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from canastasv.db import repositorio


@dataclass(frozen=True)
class FilaComparativa:
    codigo: str
    producto: str
    categoria: str
    precios: dict[str, float]  # {codigo_supermercado: precio}
    mas_barato: str | None


@dataclass(frozen=True)
class Comparativa:
    fecha: date | None
    filas: list[FilaComparativa]
    total_por_supermercado: dict[str, float]
    productos_completos: int
    total_lista_optima: float
    ahorro_vs_mejor_supermercado: float


def comparar(sesion: Session, fecha: date | None = None) -> Comparativa:
    fecha = fecha or repositorio.ultima_fecha(sesion)
    if fecha is None:
        return Comparativa(None, [], {}, 0, 0.0, 0.0)

    por_producto: dict[str, dict] = {}
    for precio in repositorio.precios_del_dia(sesion, fecha):
        producto = precio.producto
        fila = por_producto.setdefault(
            producto.codigo,
            {"producto": producto.nombre, "categoria": producto.categoria, "precios": {}},
        )
        fila["precios"][precio.supermercado.codigo] = precio.precio

    supermercados = [s.codigo for s in repositorio.listar_supermercados(sesion)]
    filas = []
    for codigo, datos in sorted(por_producto.items(), key=lambda par: (par[1]["categoria"], par[1]["producto"])):
        precios = datos["precios"]
        mas_barato = min(precios, key=precios.get) if precios else None
        filas.append(FilaComparativa(codigo, datos["producto"], datos["categoria"], precios, mas_barato))

    # Para que la suma sea justa, solo cuentan productos con precio en TODOS los supermercados.
    completas = [f for f in filas if all(s in f.precios for s in supermercados)]
    totales = {s: round(sum(f.precios[s] for f in completas), 2) for s in supermercados}
    optima = round(sum(min(f.precios.values()) for f in completas), 2)
    mejor = min(totales.values()) if completas else 0.0

    return Comparativa(
        fecha=fecha,
        filas=filas,
        total_por_supermercado=totales if completas else {},
        productos_completos=len(completas),
        total_lista_optima=optima,
        ahorro_vs_mejor_supermercado=round(mejor - optima, 2),
    )
