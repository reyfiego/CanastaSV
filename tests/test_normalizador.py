import pytest

from canastasv.emparejamiento.normalizador import extraer_tamano, normalizar
from canastasv.modelos import Tamano


def test_normalizar_quita_tildes_y_mayusculas():
    assert normalizar("  Azúcar   BLANCA ") == "azucar blanca"


@pytest.mark.parametrize(
    "nombre, esperado",
    [
        ("Arroz Blanco San Francisco 1816gr", Tamano(1816, "g")),
        ("Arroz Precocido El Pulido 1 816 g", Tamano(1816, "g")),
        ("Arroz Jasmine Dynasty -907g", Tamano(907, "g")),
        ("Azúcar Blanca 2.5 Lb", Tamano(1133.98, "g")),
        ("Harina 1 kg", Tamano(1000, "g")),
        ("Leche Entera 1 Lt", Tamano(1000, "ml")),
        ("Aceite Vegetal 750 ml", Tamano(750, "ml")),
        ("Huevos Blancos 30 Und", Tamano(30, "und")),
        ("Café 0,5 kg", Tamano(500, "g")),
    ],
)
def test_extraer_tamano(nombre, esperado):
    assert extraer_tamano(nombre) == esperado


def test_extraer_tamano_sin_tamano():
    assert extraer_tamano("Salpor De Arroz Und.") is None
