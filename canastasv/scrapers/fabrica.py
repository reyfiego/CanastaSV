"""Crea el scraper adecuado según el tipo configurado de cada supermercado."""

from canastasv.modelos import SupermercadoConfig
from canastasv.scrapers.base import Scraper
from canastasv.scrapers.http import ClienteHttp
from canastasv.scrapers.selectos import ScraperSelectos
from canastasv.scrapers.vtex import ScraperVtex

SCRAPERS_POR_TIPO: dict[str, type[Scraper]] = {
    "vtex": ScraperVtex,
    "selectos": ScraperSelectos,
}


def crear_scraper(supermercado: SupermercadoConfig, cliente: ClienteHttp) -> Scraper:
    clase = SCRAPERS_POR_TIPO.get(supermercado.tipo)
    if clase is None:
        raise ValueError(f"No hay scraper para el tipo '{supermercado.tipo}'")
    return clase(supermercado, cliente)
