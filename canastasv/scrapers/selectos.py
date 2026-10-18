"""Scraper para Súper Selectos.

Su tienda muestra los resultados de búsqueda en HTML generado por el servidor
(/products?keyword=...). Cada producto tiene un enlace con ?productId=... y su precio
aparece como texto "$0.00" dentro de la misma tarjeta.
"""

import re
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from canastasv.modelos import ProductoTienda
from canastasv.scrapers.base import Scraper

PATRON_PRECIO = re.compile(r"\$\s?(\d+(?:\.\d{1,2})?)")
# Ofertas tipo "4X$1.25": no son el precio unitario, se quitan antes de leer precios.
PATRON_MULTICOMPRA = re.compile(r"\d+\s*[xX]\s*\$\s?\d+(?:\.\d{1,2})?")
NIVELES_MAXIMOS = 6


def _id_producto(href: str) -> str | None:
    valores = parse_qs(urlparse(href).query).get("productId")
    return valores[0] if valores else None


def _ids_en(nodo: Tag) -> set[str]:
    ids = set()
    for enlace in nodo.select('a[href*="productId="]'):
        identificador = _id_producto(enlace.get("href", ""))
        if identificador:
            ids.add(identificador)
    return ids


def _tarjeta_de(enlace: Tag, identificador: str) -> Tag:
    """Sube por el árbol mientras el contenedor solo tenga este producto."""
    tarjeta = enlace
    for _ in range(NIVELES_MAXIMOS):
        padre = tarjeta.parent
        if not isinstance(padre, Tag) or _ids_en(padre) != {identificador}:
            break
        tarjeta = padre
    return tarjeta


def _leer_precios(texto: str) -> tuple[float | None, float | None]:
    texto = PATRON_MULTICOMPRA.sub(" ", texto)
    precios = [float(valor) for valor in PATRON_PRECIO.findall(texto)]
    if not precios:
        return None, None
    actual = precios[0]
    mayores = [p for p in precios[1:] if p > actual]
    return actual, (max(mayores) if mayores else None)


def parsear_productos_selectos(html: str, url_base: str) -> list[ProductoTienda]:
    sopa = BeautifulSoup(html, "html.parser")
    nombres: dict[str, str] = {}
    tarjetas: dict[str, Tag] = {}

    for enlace in sopa.select('a[href*="productId="]'):
        identificador = _id_producto(enlace.get("href", ""))
        if not identificador:
            continue
        texto = enlace.get_text(" ", strip=True)
        if texto and identificador not in nombres:
            nombres[identificador] = texto
        if identificador not in tarjetas:
            tarjetas[identificador] = _tarjeta_de(enlace, identificador)

    productos = []
    for identificador, tarjeta in tarjetas.items():
        nombre = nombres.get(identificador)
        precio, regular = _leer_precios(tarjeta.get_text(" ", strip=True))
        if not nombre or precio is None or precio <= 0:
            continue
        productos.append(
            ProductoTienda(
                id_tienda=identificador,
                nombre=nombre,
                precio=round(precio, 2),
                url=urljoin(url_base + "/", f"?productId={identificador}"),
                precio_regular=regular,
            )
        )
    return productos


class ScraperSelectos(Scraper):
    def buscar(self, termino: str) -> list[ProductoTienda]:
        respuesta = self.cliente.get(
            self.supermercado.url + "/products", params={"keyword": termino}
        )
        return parsear_productos_selectos(respuesta.text, self.supermercado.url)
