from datetime import date

from canastasv.modelos import ProductoTienda
from canastasv.servicios.comparador import comparar
from canastasv.servicios.recolector import recolectar
from canastasv.scrapers.http import ErrorDeDescarga


def _p(nombre, precio):
    return ProductoTienda(id_tienda=nombre, nombre=nombre, precio=precio, url="https://x.test")


def test_recolecta_y_compara(sesion, arroz, crear_scraper_falso):
    scrapers = [
        crear_scraper_falso("walmart", {"arroz blanco": [_p("Arroz Blanco 1816 g", 2.40)]}),
        crear_scraper_falso("selectos", {"arroz blanco": [_p("Arroz Blanco Dany 1816 g", 2.00)]}),
    ]
    resumen = recolectar(sesion, scrapers, [arroz], date(2026, 10, 18))
    assert resumen.guardados == 2

    resultado = comparar(sesion)
    assert resultado.fecha == date(2026, 10, 18)
    assert resultado.filas[0].mas_barato == "selectos"
    assert resultado.total_por_supermercado == {"selectos": 2.00, "walmart": 2.40}
    assert resultado.total_lista_optima == 2.00


def test_mismo_dia_reemplaza_el_precio(sesion, arroz, crear_scraper_falso):
    fecha = date(2026, 10, 18)
    recolectar(sesion, [crear_scraper_falso("walmart", {"arroz blanco": [_p("Arroz 1816 g", 2.40)]})], [arroz], fecha)
    recolectar(sesion, [crear_scraper_falso("walmart", {"arroz blanco": [_p("Arroz 1816 g", 2.20)]})], [arroz], fecha)
    assert comparar(sesion).filas[0].precios == {"walmart": 2.20}


def test_un_error_no_detiene_la_recoleccion(sesion, arroz, crear_scraper_falso):
    class ScraperQueFalla(crear_scraper_falso):
        def buscar(self, termino):
            raise ErrorDeDescarga("sin conexión")

    scrapers = [
        ScraperQueFalla("maxi", {}),
        crear_scraper_falso("walmart", {"arroz blanco": [_p("Arroz 1816 g", 2.40)]}),
    ]
    resumen = recolectar(sesion, scrapers, [arroz], date(2026, 10, 18))
    assert resumen.errores == ["maxi/arroz"]
    assert resumen.guardados == 1


def test_comparar_sin_datos(sesion):
    assert comparar(sesion).fecha is None
