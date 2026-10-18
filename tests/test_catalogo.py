import json

import pytest

from canastasv.catalogo import ErrorDeConfiguracion, cargar_productos, cargar_supermercados


def test_la_configuracion_real_es_valida():
    assert len(cargar_productos()) > 0
    assert {s.tipo for s in cargar_supermercados()} <= {"vtex", "selectos"}


def test_supermercados_inactivos(tmp_path):
    ruta = tmp_path / "supermercados.json"
    ruta.write_text(json.dumps([
        {"codigo": "a", "nombre": "A", "tipo": "vtex", "url": "https://a.test"},
        {"codigo": "b", "nombre": "B", "tipo": "vtex", "url": "https://b.test", "activo": False},
    ]), encoding="utf-8")
    assert [s.codigo for s in cargar_supermercados(ruta)] == ["a"]
    assert [s.codigo for s in cargar_supermercados(ruta, incluir_inactivos=True)] == ["a", "b"]


def test_unidad_invalida(tmp_path):
    ruta = tmp_path / "productos.json"
    ruta.write_text(json.dumps([{
        "codigo": "x", "nombre": "X", "categoria": "C", "busqueda": "x",
        "tamano": {"valor": 1, "unidad": "galones"},
    }]), encoding="utf-8")
    with pytest.raises(ErrorDeConfiguracion):
        cargar_productos(ruta)


def test_codigo_repetido(tmp_path):
    producto = {"codigo": "x", "nombre": "X", "categoria": "C", "busqueda": "x"}
    ruta = tmp_path / "productos.json"
    ruta.write_text(json.dumps([producto, producto]), encoding="utf-8")
    with pytest.raises(ErrorDeConfiguracion):
        cargar_productos(ruta)
