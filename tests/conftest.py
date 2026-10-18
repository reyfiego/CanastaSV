import pytest

from canastasv.db.conexion import crear_motor, fabrica_de_sesiones, inicializar
from canastasv.modelos import ProductoCanonico, ProductoTienda, SupermercadoConfig, Tamano
from canastasv.scrapers.base import Scraper


@pytest.fixture
def motor():
    motor = crear_motor(":memory:")
    inicializar(motor)
    return motor


@pytest.fixture
def sesion(motor):
    with fabrica_de_sesiones(motor)() as sesion:
        yield sesion


@pytest.fixture
def arroz():
    return ProductoCanonico(
        codigo="arroz",
        nombre="Arroz blanco",
        categoria="Granos",
        busqueda="arroz blanco",
        incluir=["arroz"],
        excluir=["precocido"],
        tamano=Tamano(1816, "g"),
    )


class ScraperFalso(Scraper):
    """Devuelve resultados fijos sin conectarse a internet."""

    def __init__(self, codigo: str, resultados: dict[str, list[ProductoTienda]]):
        super().__init__(SupermercadoConfig(codigo, codigo.title(), "vtex", "https://ejemplo.test"), None)
        self._resultados = resultados

    def buscar(self, termino):
        return self._resultados.get(termino, [])


@pytest.fixture
def crear_scraper_falso():
    return ScraperFalso
