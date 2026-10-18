from canastasv.scrapers.vtex import parsear_productos_vtex


def _item(nombre, precio, lista=None, cantidad=100):
    return {
        "productId": "1",
        "productName": nombre,
        "link": "https://tienda.test/p",
        "items": [{"sellers": [{"commertialOffer": {
            "Price": precio, "ListPrice": lista if lista is not None else precio,
            "AvailableQuantity": cantidad, "IsAvailable": cantidad > 0,
        }}]}],
    }


def test_lee_precio_y_precio_regular():
    productos = parsear_productos_vtex([_item("Arroz 1816 g", 2.4, lista=2.6)])
    assert productos[0].precio == 2.4
    assert productos[0].precio_regular == 2.6


def test_sin_descuento_no_hay_precio_regular():
    assert parsear_productos_vtex([_item("Arroz", 2.4)])[0].precio_regular is None


def test_descarta_sin_precio_sin_stock_o_mal_formados():
    datos = [_item("Agotado", 2.0, cantidad=0), _item("Gratis", 0), {"productName": "roto"}]
    assert parsear_productos_vtex(datos) == []


def test_respuesta_que_no_es_lista():
    assert parsear_productos_vtex({"error": "x"}) == []
