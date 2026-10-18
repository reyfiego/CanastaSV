from canastasv.scrapers.vtex import parsear_productos_vtex

BASE = "https://www.walmart.com.sv"


def _item(nombre, precio, lista=None, cantidad=100, link="/arroz/p"):
    return {
        "productId": "1",
        "productName": nombre,
        "link": link,
        "items": [{"sellers": [{"commertialOffer": {
            "Price": precio, "ListPrice": lista if lista is not None else precio,
            "AvailableQuantity": cantidad, "IsAvailable": cantidad > 0,
        }}]}],
    }


def test_lee_respuesta_de_intelligent_search():
    productos = parsear_productos_vtex({"products": [_item("Arroz 1816 g", 2.4, lista=2.6)]}, BASE)
    assert productos[0].precio == 2.4
    assert productos[0].precio_regular == 2.6
    assert productos[0].url == "https://www.walmart.com.sv/arroz/p"


def test_tambien_acepta_lista_directa():
    assert len(parsear_productos_vtex([_item("Arroz", 2.4)], BASE)) == 1


def test_enlace_absoluto_o_por_link_text():
    absoluto = _item("Arroz", 2.4, link="https://otra.test/x/p")
    sin_link = _item("Arroz", 2.4, link=None)
    sin_link["linkText"] = "arroz-blanco"
    urls = [p.url for p in parsear_productos_vtex([absoluto, sin_link], BASE)]
    assert urls == ["https://otra.test/x/p", "https://www.walmart.com.sv/arroz-blanco/p"]


def test_sin_descuento_no_hay_precio_regular():
    assert parsear_productos_vtex([_item("Arroz", 2.4)], BASE)[0].precio_regular is None


def test_descarta_sin_precio_sin_stock_o_mal_formados():
    datos = [_item("Agotado", 2.0, cantidad=0), _item("Gratis", 0), {"productName": "roto"}]
    assert parsear_productos_vtex(datos, BASE) == []


def test_respuesta_inesperada():
    assert parsear_productos_vtex({"error": "x"}, BASE) == []
