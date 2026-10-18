"""Entrega una sesión de base de datos a cada petición y la cierra al terminar."""

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session


def obtener_vigentes(request: Request) -> set[str]:
    """Códigos de los productos que siguen en la configuración."""
    return request.app.state.vigentes


def obtener_sesion(request: Request) -> Iterator[Session]:
    fabrica = request.app.state.fabrica_sesiones
    with fabrica() as sesion:
        yield sesion
