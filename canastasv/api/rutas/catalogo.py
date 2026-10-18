"""Rutas de productos y supermercados."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from canastasv.api.dependencias import obtener_sesion, obtener_vigentes
from canastasv.api.esquemas import ProductoOut, PuntoHistorialOut, SupermercadoOut
from canastasv.db import repositorio

router = APIRouter(prefix="/api", tags=["catálogo"])


@router.get("/supermercados", response_model=list[SupermercadoOut])
def supermercados(sesion: Session = Depends(obtener_sesion)):
    return [SupermercadoOut(codigo=s.codigo, nombre=s.nombre) for s in repositorio.listar_supermercados(sesion)]


@router.get("/productos", response_model=list[ProductoOut])
def productos(sesion: Session = Depends(obtener_sesion), vigentes: set[str] = Depends(obtener_vigentes)):
    """Productos vigentes. El historial de los que ya no están sigue disponible por su código."""
    return [
        ProductoOut(codigo=p.codigo, nombre=p.nombre, categoria=p.categoria)
        for p in repositorio.listar_productos(sesion)
        if p.codigo in vigentes
    ]


@router.get("/productos/{codigo}/historial", response_model=list[PuntoHistorialOut])
def historial(codigo: str, sesion: Session = Depends(obtener_sesion)):
    puntos = repositorio.historial(sesion, codigo)
    if not puntos and codigo not in {p.codigo for p in repositorio.listar_productos(sesion)}:
        raise HTTPException(status_code=404, detail=f"No existe el producto '{codigo}'")
    return [
        PuntoHistorialOut(
            fecha=p.fecha,
            supermercado=p.supermercado.codigo,
            precio=p.precio,
            precio_regular=p.precio_regular,
            nombre_en_tienda=p.nombre_en_tienda,
            url=p.url,
        )
        for p in puntos
    ]
