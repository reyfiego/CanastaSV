"""Elige, entre los resultados de una tienda, el que corresponde a un producto canónico."""

from dataclasses import dataclass

from canastasv.emparejamiento.normalizador import extraer_tamano, normalizar
from canastasv.modelos import ProductoCanonico, ProductoTienda, Tamano

TOLERANCIA_TAMANO = 0.12  # 12 % arriba o abajo del tamaño buscado


@dataclass(frozen=True)
class Coincidencia:
    producto: ProductoTienda
    tamano: Tamano | None


def _cumple_palabras(nombre: str, canonico: ProductoCanonico) -> bool:
    texto = normalizar(nombre)
    if any(normalizar(palabra) not in texto for palabra in canonico.incluir):
        return False
    return not any(normalizar(palabra) in texto for palabra in canonico.excluir)


def _cumple_tamano(tamano: Tamano | None, objetivo: Tamano | None) -> bool:
    if objetivo is None:
        return True
    if tamano is None or tamano.unidad != objetivo.unidad:
        return False
    return abs(tamano.valor - objetivo.valor) <= objetivo.valor * TOLERANCIA_TAMANO


def emparejar(
    canonico: ProductoCanonico, candidatos: list[ProductoTienda]
) -> Coincidencia | None:
    """Devuelve el candidato más barato que cumple palabras clave y tamaño, o None."""
    validos = []
    for candidato in candidatos:
        if not _cumple_palabras(candidato.nombre, canonico):
            continue
        tamano = extraer_tamano(candidato.nombre)
        if _cumple_tamano(tamano, canonico.tamano):
            validos.append(Coincidencia(producto=candidato, tamano=tamano))
    if not validos:
        return None
    return min(validos, key=lambda c: c.producto.precio)
