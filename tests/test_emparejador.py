from canastasv.emparejamiento.emparejador import emparejar
from canastasv.modelos import ProductoTienda


def _p(nombre, precio):
    return ProductoTienda(id_tienda=nombre, nombre=nombre, precio=precio, url="")


def test_elige_el_mas_barato_que_cumple(arroz):
    candidatos = [
        _p("Arroz Blanco As De Oros 1816 Gr", 2.60),
        _p("Arroz Blanco San Francisco 1816gr", 2.40),
        _p("Arroz Omoa Precocido 1814 g", 2.10),  # excluido por palabra
        _p("Arroz Blanco Dany 454 g", 0.50),      # tamaño fuera de tolerancia
    ]
    resultado = emparejar(arroz, candidatos)
    assert resultado is not None
    assert resultado.producto.nombre == "Arroz Blanco San Francisco 1816gr"


def test_sin_coincidencia_devuelve_none(arroz):
    assert emparejar(arroz, [_p("Frijol Rojo 454 g", 1.0)]) is None


def test_ignora_tildes_en_palabras_clave(arroz):
    assert emparejar(arroz, [_p("ARRÓZ BLANCO 4 lb", 2.0)]) is not None
