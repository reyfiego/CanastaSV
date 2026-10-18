"""Estructuras de datos que viajan entre módulos (sin dependencia de la base de datos)."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Tamano:
    valor: float
    unidad: str  # "g", "ml" o "und"


@dataclass(frozen=True)
class SupermercadoConfig:
    codigo: str
    nombre: str
    tipo: str
    url: str


@dataclass(frozen=True)
class ProductoCanonico:
    """Producto de la canasta que queremos comparar entre supermercados."""

    codigo: str
    nombre: str
    categoria: str
    busqueda: str
    incluir: list[str] = field(default_factory=list)
    excluir: list[str] = field(default_factory=list)
    tamano: Optional[Tamano] = None


@dataclass(frozen=True)
class ProductoTienda:
    """Un producto tal como aparece en la tienda en línea de un supermercado."""

    id_tienda: str
    nombre: str
    precio: float
    url: str
    precio_regular: Optional[float] = None
