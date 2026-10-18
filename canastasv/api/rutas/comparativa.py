"""Ruta de la comparativa diaria de precios."""

from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from canastasv.api.dependencias import obtener_sesion
from canastasv.api.esquemas import ComparativaOut
from canastasv.servicios.comparador import comparar

router = APIRouter(prefix="/api", tags=["comparativa"])


@router.get("/comparativa", response_model=ComparativaOut)
def comparativa(fecha: date | None = None, sesion: Session = Depends(obtener_sesion)):
    """Comparativa del día indicado, o del último día con datos si no se indica."""
    return asdict(comparar(sesion, fecha))
