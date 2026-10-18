from canastasv.scrapers.selectos import parsear_productos_selectos

HTML = """
<div class="grid">
  <div class="card">
    <a href="/?productId=3545"><img src="x.jpg"></a>
    <strong>$2.00</strong>
    <h5><a href="/?productId=3545">Arroz Blanco Dany 1816 g</a></h5>
  </div>
  <div class="card">
    <a href="/?productId=117624"><img src="y.jpg"></a>
    <strong>$8.45</strong><span>$9.10</span><span>Ahorras $0.65</span>
    <h5><a href="/?productId=117624">Aceite Vegetal 3 L</a></h5>
  </div>
  <div class="card">
    <a href="/?productId=3523"><img src="z.jpg"></a>
    <span>Seleccione 4X$1.25</span><strong>$0.40</strong>
    <h5><a href="/?productId=3523">Sopa Instantánea 64 g</a></h5>
  </div>
</div>
"""


def test_lee_cada_tarjeta_por_separado():
    productos = {p.id_tienda: p for p in parsear_productos_selectos(HTML, "https://www.superselectos.com")}
    assert set(productos) == {"3545", "117624", "3523"}
    assert productos["3545"].nombre == "Arroz Blanco Dany 1816 g"
    assert productos["3545"].precio == 2.00
    assert productos["3545"].url == "https://www.superselectos.com/?productId=3545"


def test_precio_con_descuento():
    aceite = next(p for p in parsear_productos_selectos(HTML, "https://s.test") if p.id_tienda == "117624")
    assert aceite.precio == 8.45
    assert aceite.precio_regular == 9.10


def test_ignora_oferta_multicompra():
    sopa = next(p for p in parsear_productos_selectos(HTML, "https://s.test") if p.id_tienda == "3523")
    assert sopa.precio == 0.40


def test_pagina_sin_resultados():
    assert parsear_productos_selectos("<h1>No se encontraron resultados...</h1>", "https://s.test") == []
