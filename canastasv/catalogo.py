"""Carga y valida los archivos de configuración de productos y supermercados."""

import json
from pathlib import Path

from canastasv.config import DIR_CONFIG
from canastasv.modelos import ProductoCanonico, SupermercadoConfig, Tamano

UNIDADES_VALIDAS = {"g", "ml", "und"}
TIPOS_VALIDOS = {"vtex", "selectos"}


class ErrorDeConfiguracion(ValueError):
    """Se lanza cuando un archivo de configuración tiene datos inválidos."""


def _leer_json(ruta: Path) -> list[dict]:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError as error:
        raise ErrorDeConfiguracion(f"No existe el archivo {ruta}") from error
    except json.JSONDecodeError as error:
        raise ErrorDeConfiguracion(f"{ruta} no es un JSON válido: {error}") from error
    if not isinstance(datos, list):
        raise ErrorDeConfiguracion(f"{ruta} debe contener una lista")
    return datos


def cargar_productos(ruta: Path = DIR_CONFIG / "productos.json") -> list[ProductoCanonico]:
    productos = []
    codigos = set()
    for entrada in _leer_json(ruta):
        for clave in ("codigo", "nombre", "categoria", "busqueda"):
            if not entrada.get(clave):
                raise ErrorDeConfiguracion(f"Producto sin '{clave}': {entrada}")
        if entrada["codigo"] in codigos:
            raise ErrorDeConfiguracion(f"Código de producto repetido: {entrada['codigo']}")
        codigos.add(entrada["codigo"])

        tamano = None
        if entrada.get("tamano"):
            unidad = entrada["tamano"].get("unidad")
            if unidad not in UNIDADES_VALIDAS:
                raise ErrorDeConfiguracion(
                    f"Unidad inválida en {entrada['codigo']}: {unidad} (usa g, ml o und)"
                )
            tamano = Tamano(valor=float(entrada["tamano"]["valor"]), unidad=unidad)

        productos.append(
            ProductoCanonico(
                codigo=entrada["codigo"],
                nombre=entrada["nombre"],
                categoria=entrada["categoria"],
                busqueda=entrada["busqueda"],
                incluir=list(entrada.get("incluir", [])),
                excluir=list(entrada.get("excluir", [])),
                tamano=tamano,
            )
        )
    return productos


def cargar_supermercados(
    ruta: Path = DIR_CONFIG / "supermercados.json",
) -> list[SupermercadoConfig]:
    supermercados = []
    for entrada in _leer_json(ruta):
        for clave in ("codigo", "nombre", "tipo", "url"):
            if not entrada.get(clave):
                raise ErrorDeConfiguracion(f"Supermercado sin '{clave}': {entrada}")
        if entrada["tipo"] not in TIPOS_VALIDOS:
            raise ErrorDeConfiguracion(f"Tipo de scraper desconocido: {entrada['tipo']}")
        supermercados.append(
            SupermercadoConfig(
                codigo=entrada["codigo"],
                nombre=entrada["nombre"],
                tipo=entrada["tipo"],
                url=entrada["url"].rstrip("/"),
            )
        )
    return supermercados
