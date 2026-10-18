from datetime import date

from fastapi.testclient import TestClient

from canastasv.api.app import crear_app
from canastasv.db.conexion import fabrica_de_sesiones
from canastasv.modelos import ProductoTienda
from canastasv.servicios.recolector import recolectar


def _cliente(motor):
    return TestClient(crear_app(motor))


def test_salud(motor):
    assert _cliente(motor).get("/api/salud").json()["estado"] == "ok"


def test_comparativa_e_historial(motor, arroz, crear_scraper_falso):
    with fabrica_de_sesiones(motor)() as sesion:
        scraper = crear_scraper_falso(
            "walmart", {"arroz blanco": [ProductoTienda("1", "Arroz 1816 g", 2.4, "https://x.test")]}
        )
        recolectar(sesion, [scraper], [arroz], date(2026, 10, 18))

    cliente = _cliente(motor)
    comparativa = cliente.get("/api/comparativa").json()
    assert comparativa["filas"][0]["precios"] == {"walmart": 2.4}

    historial = cliente.get("/api/productos/arroz/historial").json()
    assert historial[0]["precio"] == 2.4


def test_historial_de_producto_inexistente(motor):
    assert _cliente(motor).get("/api/productos/no-existe/historial").status_code == 404


def test_sirve_el_dashboard(motor):
    respuesta = _cliente(motor).get("/")
    assert respuesta.status_code == 200
    assert "CanastaSV" in respuesta.text
