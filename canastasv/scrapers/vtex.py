"""Scraper para tiendas en la plataforma VTEX (Walmart, Maxi Despensa, Despensa de Don Juan).

Usa la API pública "Intelligent Search" de VTEX, la misma que alimenta el buscador
de la tienda. Devuelve JSON, acepta búsquedas de varias palabras y no requiere leer HTML.
"""

from typing import Any

from canastasv.modelos import ProductoTienda
from canastasv.scrapers.base import Scraper
from canastasv.scrapers.http import ErrorDeDescarga

RUTA_BUSQUEDA = "/api/io/_v/api/intelligent-search/product_search/"
MAXIMO_RESULTADOS = 30


def _url_producto(item: dict, url_base: str) -> str:
    enlace = str(item.get("link") or "")
    if enlace.startswith("http"):
        return enlace
    if enlace.startswith("/"):
        return url_base + enlace
    if item.get("linkText"):
        return f"{url_base}/{item['linkText']}/p"
    return url_base


def parsear_productos_vtex(datos: Any, url_base: str = "") -> list[ProductoTienda]:
    """Convierte la respuesta de VTEX en ProductoTienda, ignorando lo que no tenga precio.

    Acepta tanto la respuesta de Intelligent Search ({"products": [...]}) como una lista directa.
    """
    if isinstance(datos, dict):
        datos = datos.get("products")
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
                url=_url_producto(item, url_base),
                precio_regular=round(regular, 2) if regular and regular > precio else None,
            )
        )
    return productos


class ScraperVtex(Scraper):
    def buscar(self, termino: str) -> list[ProductoTienda]:
        url = self.supermercado.url + RUTA_BUSQUEDA
        params = {"query": termino, "count": MAXIMO_RESULTADOS}
        respuesta = self.cliente.get(url, params=params)
        try:
            datos = respuesta.json()
        except ValueError as error:
            raise ErrorDeDescarga(f"{self.supermercado.nombre} no devolvió JSON válido") from error
        return parsear_productos_vtex(datos, self.supermercado.url)
