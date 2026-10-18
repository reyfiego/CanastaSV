"""Interfaz común que implementa cada scraper."""

from abc import ABC, abstractmethod

from canastasv.modelos import ProductoTienda, SupermercadoConfig
from canastasv.scrapers.http import ClienteHttp


class Scraper(ABC):
    def __init__(self, supermercado: SupermercadoConfig, cliente: ClienteHttp):
        self.supermercado = supermercado
        self.cliente = cliente

    @abstractmethod
    def buscar(self, termino: str) -> list[ProductoTienda]:
        """Busca un término en la tienda y devuelve los productos encontrados con precio."""
