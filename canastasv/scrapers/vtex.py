"""Scraper para tiendas en la plataforma VTEX (Walmart, Maxi Despensa, Despensa de Don Juan).

Usa dos APIs públicas de VTEX que devuelven JSON:

1. "Intelligent Search", la misma del buscador de la tienda. Acepta búsquedas de varias palabras.
2. La API de catálogo, como respaldo. En estas tiendas solo acepta una palabra, así que se busca
   con la primera palabra del término y el emparejador filtra el resto.

Si la primera falla, el scraper se pasa a la segunda para el resto de la recolección.
"""

import logging
from typing import Any

from canastasv.modelos import ProductoTienda
from canastasv.scrapers.base import Scraper
from canastasv.scrapers.http import ErrorDeDescarga

log = logging.getLogger(__name__)

RUTA_INTELLIGENT_SEARCH = "/api/io/_v/api/intelligent-search/product_search/"
RUTA_CATALOGO = "/api/catalog_system/pub/products/search"
MAXIMO_RESULTADOS = 20


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

    Acepta tanto la respuesta de Intelligent Search ({"products": [...]}) como la del catálogo (lista).
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
    def __init__(self, supermercado, cliente):
        super().__init__(supermercado, cliente)
        self._usar_intelligent_search = True

    def _json(self, ruta: str, params: dict) -> Any:
        respuesta = self.cliente.get(self.supermercado.url + ruta, params=params)
        try:
            return respuesta.json()
        except ValueError as error:
            raise ErrorDeDescarga(f"{self.supermercado.nombre} no devolvió JSON válido") from error

    def _buscar_intelligent_search(self, termino: str) -> Any:
        return self._json(RUTA_INTELLIGENT_SEARCH, {"query": termino, "count": MAXIMO_RESULTADOS})

    def _buscar_catalogo(self, termino: str) -> Any:
        primera_palabra = termino.split()[0]
        return self._json(
            RUTA_CATALOGO, {"ft": primera_palabra, "_from": 0, "_to": MAXIMO_RESULTADOS - 1}
        )

    def buscar(self, termino: str) -> list[ProductoTienda]:
        if self._usar_intelligent_search:
            try:
                return parsear_productos_vtex(self._buscar_intelligent_search(termino), self.supermercado.url)
            except ErrorDeDescarga as error:
                log.warning(
                    "%s: Intelligent Search falló (%s). Se usará la API de catálogo.",
                    self.supermercado.nombre, error,
                )
                self._usar_intelligent_search = False
        return parsear_productos_vtex(self._buscar_catalogo(termino), self.supermercado.url)
