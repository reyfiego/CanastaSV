"""Scraper para tiendas en la plataforma VTEX (Walmart, Maxi Despensa, Despensa de Don Juan).

VTEX expone una API pública de catálogo que devuelve JSON, así que no hace falta
leer HTML: es más rápido, más estable y menos pesado para el sitio.
"""

from typing import Any

from canastasv.modelos import ProductoTienda
from canastasv.scrapers.base import Scraper
from canastasv.scrapers.http import ErrorDeDescarga

RUTA_BUSQUEDA = "/api/catalog_system/pub/products/search"
MAXIMO_RESULTADOS = 30


def parsear_productos_vtex(datos: Any) -> list[ProductoTienda]:
    """Convierte la respuesta JSON de VTEX en ProductoTienda, ignorando lo que no tenga precio."""
    if not isinstance(datos, list):
        return []
    productos = []
    for item in datos:
        try:
            oferta = item["items"][0]["sellers"][0]["commertialOffer"]
            precio = float(oferta.get("Price") or 0)
            disponible = oferta.get("IsAvailable", True) and (oferta.get("AvailableQuantity") or 0) > 0
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if precio <= 0 or not disponible:
            continue
        regular = oferta.get("ListPrice")
        try:
            regular = float(regular) if regular else None
        except (TypeError, ValueError):
            regular = None
        productos.append(
            ProductoTienda(
                id_tienda=str(item.get("productId", "")),
                nombre=str(item.get("productName", "")).strip(),
                precio=round(precio, 2),
                url=str(item.get("link", "")),
                precio_regular=round(regular, 2) if regular and regular > precio else None,
            )
        )
    return productos


class ScraperVtex(Scraper):
    def buscar(self, termino: str) -> list[ProductoTienda]:
        url = self.supermercado.url + RUTA_BUSQUEDA
        params = {"ft": termino, "_from": 0, "_to": MAXIMO_RESULTADOS - 1}
        respuesta = self.cliente.get(url, params=params)
        try:
            datos = respuesta.json()
        except ValueError as error:
            raise ErrorDeDescarga(f"{self.supermercado.nombre} no devolvió JSON válido") from error
        return parsear_productos_vtex(datos)
