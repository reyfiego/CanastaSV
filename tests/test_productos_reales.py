"""Verifica config/productos.json contra nombres reales vistos en las tiendas (18 oct 2026).

Si una tienda cambia sus nombres y un producto deja de emparejar, estas pruebas ayudan a
ajustar las palabras clave sin tener que esperar a la recolección diaria.
"""

import pytest

from canastasv.catalogo import cargar_productos
from canastasv.emparejamiento.emparejador import emparejar
from canastasv.modelos import ProductoTienda

PRODUCTOS = {p.codigo: p for p in cargar_productos()}


def _candidatos(*pares):
    return [ProductoTienda(id_tienda=str(i), nombre=n, precio=p, url="") for i, (n, p) in enumerate(pares)]


CASOS = [
    (
        "huevos-30",
        [
            ("Huevo Dino Mania Smashers", 25.0),
            ("Huevo Dino Island Smashers", 5.5),
            ("Huevo Mediano Marron Frescos 30 U", 5.7),
            ("Huevo Grande Marron Frescos 30 U", 5.95),
            ("Huevo Grande Marron Frescos 15 U", 3.1),
            ("Mayonesa Hellmanns Contiene Huevos De Campo Doypack - 880 g", 4.0),
        ],
        "Huevo Grande Marron Frescos 30 U",
    ),
    (
        "pasta-espagueti-200g",
        [
            ("Salsa Mccormick Espagueti - 38 g", 1.7),
            ("Pasta Larga Ina Espagueti 3 Pack 600g", 1.55),
            ("Pasta larga Ina Espagueti - 200 g", 0.61),
            ("Pasta Espagueti Ina Lasagna Lisa - 400 g", 1.85),
            ("Pasta Roma espagueti libre de gluten - 250 g", 2.35),
        ],
        "Pasta larga Ina Espagueti - 200 g",
    ),
    (
        "avena-hojuela-350g",
        [
            ("Avena Tosh Cup Avena Arándanos -40 g", 1.35),
            ("Avena Valena Hojuela 350gr", 1.0),
            ("Avena Valena Molida 250gr", 1.0),
            ("Avena Great Value Maple Brownsugar 430gr", 2.6),
            ("Avena Mosh Quaker 4000 Gr", 12.85),
        ],
        "Avena Valena Hojuela 350gr",
    ),
    (
        "cafe-instantaneo-170g",
        [
            ("Café SonCafé Tostado Molido 340 g", 7.95),
            ("Café ColCafé Capuccino Moca - 108 g", 3.45),
            ("Café ColCafé Mezcla Cappuccino - 108 g", 3.45),
            ("Zapatilla No Cafe", 10.0),
            ("Café ColCafé Clásico Instantáneo Bote - 170 g", 6.4),
        ],
        "Café ColCafé Clásico Instantáneo Bote - 170 g",
    ),
    (
        "detergente-polvo-1-8kg",
        [
            ("Detergente Ultraklin Fuerza Intensa 1.8Kg", 2.7),
            ("Polanco Detergente 4En1 8 Lt", 13.85),
            ("Detergente En Polvo Suli Natural 9000gr", 8.65),
            ("Detergente En Polvo Suli Natural 2500gr", 2.49),
            ("Detergente Liquido Woolite Tld 1800 ml", 9.2),
        ],
        "Detergente Ultraklin Fuerza Intensa 1.8Kg",
    ),
]


@pytest.mark.parametrize("codigo, candidatos, esperado", CASOS, ids=[c[0] for c in CASOS])
def test_empareja_el_producto_correcto(codigo, candidatos, esperado):
    resultado = emparejar(PRODUCTOS[codigo], _candidatos(*candidatos))
    assert resultado is not None, f"{codigo} no encontró coincidencia"
    assert resultado.producto.nombre == esperado
