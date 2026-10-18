"""Crea la aplicación FastAPI. Ejecutar con: uvicorn canastasv.api.app:app --reload

Sirve la API en /api y el dashboard web (carpeta frontend/) en la raíz.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Engine

from canastasv import __version__
from canastasv.api.rutas import catalogo, comparativa
from canastasv.config import RAIZ_PROYECTO, cargar_ajustes
from canastasv.db.conexion import crear_motor, fabrica_de_sesiones, inicializar

DIR_FRONTEND = RAIZ_PROYECTO / "frontend"


def crear_app(motor: Engine | None = None) -> FastAPI:
    motor = motor or crear_motor(cargar_ajustes().ruta_db)
    inicializar(motor)

    aplicacion = FastAPI(title="CanastaSV", version=__version__)
    aplicacion.state.fabrica_sesiones = fabrica_de_sesiones(motor)
    aplicacion.include_router(catalogo.router)
    aplicacion.include_router(comparativa.router)

    @aplicacion.get("/api/salud", tags=["sistema"])
    def salud():
        return {"estado": "ok", "version": __version__}

    # Va al final: las rutas /api/... tienen prioridad sobre los archivos estáticos.
    if DIR_FRONTEND.is_dir():
        aplicacion.mount("/", StaticFiles(directory=DIR_FRONTEND, html=True), name="frontend")

    return aplicacion


app = crear_app()
