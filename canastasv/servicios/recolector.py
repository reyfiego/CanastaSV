"""Recorre cada producto en cada supermercado, empareja y guarda el precio del día."""

import logging
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from canastasv.db import repositorio
from canastasv.emparejamiento.emparejador import emparejar
from canastasv.modelos import ProductoCanonico
from canastasv.scrapers.base import Scraper
from canastasv.scrapers.http import ErrorDeDescarga

log = logging.getLogger(__name__)


@dataclass
class Resumen:
    guardados: int = 0
    sin_coincidencia: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)

    @property
    def hubo_datos(self) -> bool:
        return self.guardados > 0


def recolectar(
    sesion: Session,
    scrapers: list[Scraper],
    canonicos: list[ProductoCanonico],
    fecha: date,
) -> Resumen:
    supermercados = repositorio.sincronizar_supermercados(
        sesion, [scraper.supermercado for scraper in scrapers]
    )
    productos = repositorio.sincronizar_productos(sesion, canonicos)
    resumen = Resumen()

    for scraper in scrapers:
        tienda = scraper.supermercado
        for canonico in canonicos:
            etiqueta = f"{tienda.codigo}/{canonico.codigo}"
            try:
                candidatos = scraper.buscar(canonico.busqueda)
            except ErrorDeDescarga as error:
                log.warning("Error en %s: %s", etiqueta, error)
                resumen.errores.append(etiqueta)
                continue

            coincidencia = emparejar(canonico, candidatos)
            if coincidencia is None:
                log.info("Sin coincidencia en %s (%d candidatos)", etiqueta, len(candidatos))
                resumen.sin_coincidencia.append(etiqueta)
                continue

            repositorio.guardar_precio(
                sesion,
                productos[canonico.codigo],
                supermercados[tienda.codigo],
                coincidencia.producto,
                fecha,
            )
            resumen.guardados += 1
            log.info("%s -> %s $%.2f", etiqueta, coincidencia.producto.nombre, coincidencia.producto.precio)

        sesion.commit()  # se guarda por tienda para no perder lo avanzado si algo falla

    return resumen
