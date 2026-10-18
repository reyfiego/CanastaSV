"""Formas de las respuestas JSON de la API."""

from datetime import date

from pydantic import BaseModel


class SupermercadoOut(BaseModel):
    codigo: str
    nombre: str


class ProductoOut(BaseModel):
    codigo: str
    nombre: str
    categoria: str


class FilaComparativaOut(BaseModel):
    codigo: str
    producto: str
    categoria: str
    precios: dict[str, float]
    mas_barato: str | None
    dudosos: dict[str, float] = {}


class ComparativaOut(BaseModel):
    fecha: date | None
    supermercados: list[str]
    filas: list[FilaComparativaOut]
    total_por_supermercado: dict[str, float]
    productos_completos: int
    total_lista_optima: float
    ahorro_vs_mejor_supermercado: float


class PuntoHistorialOut(BaseModel):
    fecha: date
    supermercado: str
    precio: float
    precio_regular: float | None
    nombre_en_tienda: str
    url: str
