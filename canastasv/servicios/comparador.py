"""Compara los precios de un día: más barato por producto, costo por súper y lista óptima."""

from dataclasses import dataclass, field
from datetime import date
from statistics import median

from sqlalchemy.orm import Session

from canastasv.db import repositorio

# Un precio por debajo de esta fracción de la mediana de los demás súper se considera dudoso
# (por ejemplo, un error de la tienda: aceite a $0.25 cuando en los demás cuesta $1.80).
UMBRAL_ATIPICO = 0.5


@dataclass(frozen=True)
class FilaComparativa:
    codigo: str
    producto: str
    categoria: str
    precios: dict[str, float]  # {codigo_supermercado: precio} que sí entran en la comparación
    mas_barato: str | None
    dudosos: dict[str, float] = field(default_factory=dict)  # precios apartados por atípicos


@dataclass(frozen=True)
class Comparativa:
    fecha: date | None
    supermercados: list[str]  # códigos con precios ese día
    filas: list[FilaComparativa]
    total_por_supermercado: dict[str, float]
    productos_completos: int
    total_lista_optima: float
    ahorro_vs_mejor_supermercado: float


def separar_dudosos(precios: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    """Aparta los precios muy por debajo de la mediana de los demás supermercados.

    Con menos de 3 precios no se puede saber cuál está mal, así que no se aparta ninguno.
    """
    if len(precios) < 3:
        return dict(precios), {}
    validos, dudosos = {}, {}
    for codigo, precio in precios.items():
        otros = [p for c, p in precios.items() if c != codigo]
        if precio < median(otros) * UMBRAL_ATIPICO:
            dudosos[codigo] = precio
        else:
            validos[codigo] = precio
    return validos, dudosos


def comparar(sesion: Session, fecha: date | None = None) -> Comparativa:
    fecha = fecha or repositorio.ultima_fecha(sesion)
    if fecha is None:
        return Comparativa(None, [], [], {}, 0, 0.0, 0.0)

    por_producto: dict[str, dict] = {}
    for precio in repositorio.precios_del_dia(sesion, fecha):
        producto = precio.producto
        fila = por_producto.setdefault(
            producto.codigo,
            {"producto": producto.nombre, "categoria": producto.categoria, "precios": {}},
        )
        fila["precios"][precio.supermercado.codigo] = precio.precio

    # Solo cuentan los supermercados que tuvieron al menos un precio ese día: uno desactivado
    # o que falló completo no debe dejar la comparación vacía.
    supermercados = sorted({s for datos in por_producto.values() for s in datos["precios"]})
    filas = []
    for codigo, datos in sorted(por_producto.items(), key=lambda par: (par[1]["categoria"], par[1]["producto"])):
        precios, dudosos = separar_dudosos(datos["precios"])
        mas_barato = min(precios, key=precios.get) if precios else None
        filas.append(FilaComparativa(codigo, datos["producto"], datos["categoria"], precios, mas_barato, dudosos))

    # Para que la suma sea justa, solo cuentan productos con precio válido en TODOS los supermercados.
    completas = [f for f in filas if all(s in f.precios for s in supermercados)]
    totales = {s: round(sum(f.precios[s] for f in completas), 2) for s in supermercados}
    optima = round(sum(min(f.precios.values()) for f in completas), 2)
    mejor = min(totales.values()) if completas else 0.0

    return Comparativa(
        fecha=fecha,
        supermercados=supermercados,
        filas=filas,
        total_por_supermercado=totales if completas else {},
        productos_completos=len(completas),
        total_lista_optima=optima,
        ahorro_vs_mejor_supermercado=round(mejor - optima, 2),
    )
