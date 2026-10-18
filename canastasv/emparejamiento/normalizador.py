"""Limpieza de nombres de producto y lectura de tamaños ("1816 g", "2.5 Lb", "1 Lt", "30 Uds")."""

import re
import unicodedata

from canastasv.modelos import Tamano

GRAMOS_POR_LIBRA = 453.592
GRAMOS_POR_ONZA = 28.3495

# unidad escrita -> (unidad base, factor de conversión)
UNIDADES = {
    "kg": ("g", 1000.0), "kgs": ("g", 1000.0), "kilo": ("g", 1000.0), "kilos": ("g", 1000.0),
    "g": ("g", 1.0), "gr": ("g", 1.0), "grs": ("g", 1.0), "gramos": ("g", 1.0),
    "lb": ("g", GRAMOS_POR_LIBRA), "lbs": ("g", GRAMOS_POR_LIBRA),
    "libra": ("g", GRAMOS_POR_LIBRA), "libras": ("g", GRAMOS_POR_LIBRA),
    "oz": ("g", GRAMOS_POR_ONZA), "onzas": ("g", GRAMOS_POR_ONZA),
    "ml": ("ml", 1.0),
    "l": ("ml", 1000.0), "lt": ("ml", 1000.0), "lts": ("ml", 1000.0),
    "litro": ("ml", 1000.0), "litros": ("ml", 1000.0),
    "und": ("und", 1.0), "unds": ("und", 1.0), "ud": ("und", 1.0), "uds": ("und", 1.0),
    "unidad": ("und", 1.0), "unidades": ("und", 1.0), "u": ("und", 1.0),
}
# En unidades pequeñas, "1,816 g" o "1.816 g" es un separador de miles, no un decimal.
UNIDADES_PEQUENAS = {"g", "gr", "grs", "gramos", "ml"}

_PATRON_MILES_ESPACIO = re.compile(r"(?<=\d) (?=\d{3}\b)")
_PATRON_TAMANO = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(" + "|".join(sorted(UNIDADES, key=len, reverse=True)) + r")\b"
)
_PATRON_MULTIPACK = re.compile(r"\b\d+\s*-?\s*pack\b|\bpack\s*(de\s*)?\d+\b|\b\d+\s*x\s*\d")


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y con espacios simples."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.lower()).strip()


def es_multipack(nombre: str) -> bool:
    """True si el nombre parece un paquete de varias unidades ("2 Pack", "Pack de 6", "3x200 g")."""
    return bool(_PATRON_MULTIPACK.search(normalizar(nombre)))


def _a_numero(numero: str, unidad: str) -> float:
    entero, _, decimales = numero.replace(",", ".").partition(".")
    if decimales and len(decimales) == 3 and unidad in UNIDADES_PEQUENAS:
        return float(entero + decimales)
    return float(numero.replace(",", "."))


def extraer_tamano(nombre: str) -> Tamano | None:
    """Devuelve el último tamaño que aparezca en el nombre, convertido a g, ml o und."""
    texto = _PATRON_MILES_ESPACIO.sub("", normalizar(nombre))
    coincidencias = _PATRON_TAMANO.findall(texto)
    if not coincidencias:
        return None
    numero, unidad = coincidencias[-1]
    base, factor = UNIDADES[unidad]
    return Tamano(valor=round(_a_numero(numero, unidad) * factor, 2), unidad=base)
