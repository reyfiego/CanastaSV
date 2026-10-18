"""Limpieza de nombres de producto y lectura de tamaños ("1816 g", "2.5 Lb", "1 Lt", "30 Und")."""

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
    "und": ("und", 1.0), "unidades": ("und", 1.0), "unidad": ("und", 1.0), "u": ("und", 1.0),
}

_PATRON_MILES = re.compile(r"(?<=\d) (?=\d{3}\b)")
_PATRON_TAMANO = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(" + "|".join(sorted(UNIDADES, key=len, reverse=True)) + r")\b"
)


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y con espacios simples."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.lower()).strip()


def extraer_tamano(nombre: str) -> Tamano | None:
    """Devuelve el último tamaño que aparezca en el nombre, convertido a g, ml o und."""
    texto = _PATRON_MILES.sub("", normalizar(nombre))
    coincidencias = _PATRON_TAMANO.findall(texto)
    if not coincidencias:
        return None
    numero, unidad = coincidencias[-1]
    base, factor = UNIDADES[unidad]
    return Tamano(valor=round(float(numero.replace(",", ".")) * factor, 2), unidad=base)
