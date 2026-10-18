"""Operaciones de lectura y escritura sobre la base de datos."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from canastasv.db.tablas import Precio, Producto, Supermercado
from canastasv.modelos import ProductoCanonico, ProductoTienda, SupermercadoConfig


def sincronizar_supermercados(sesion: Session, configs: list[SupermercadoConfig]) -> dict[str, Supermercado]:
    """Crea o actualiza los supermercados de la configuración. Devuelve {codigo: fila}."""
    filas = {}
    for config in configs:
        fila = sesion.scalar(select(Supermercado).where(Supermercado.codigo == config.codigo))
        if fila is None:
            fila = Supermercado(codigo=config.codigo)
            sesion.add(fila)
        fila.nombre = config.nombre
        fila.url = config.url
        filas[config.codigo] = fila
    sesion.flush()
    return filas


def sincronizar_productos(sesion: Session, canonicos: list[ProductoCanonico]) -> dict[str, Producto]:
    """Crea o actualiza los productos canónicos. Devuelve {codigo: fila}."""
    filas = {}
    for canonico in canonicos:
        fila = sesion.scalar(select(Producto).where(Producto.codigo == canonico.codigo))
        if fila is None:
            fila = Producto(codigo=canonico.codigo)
            sesion.add(fila)
        fila.nombre = canonico.nombre
        fila.categoria = canonico.categoria
        fila.tamano_valor = canonico.tamano.valor if canonico.tamano else None
        fila.tamano_unidad = canonico.tamano.unidad if canonico.tamano else None
        filas[canonico.codigo] = fila
    sesion.flush()
    return filas


def guardar_precio(
    sesion: Session,
    producto: Producto,
    supermercado: Supermercado,
    encontrado: ProductoTienda,
    fecha: date,
) -> Precio:
    """Guarda el precio del día. Si ya había uno ese día, lo reemplaza."""
    fila = sesion.scalar(
        select(Precio).where(
            Precio.producto_id == producto.id,
            Precio.supermercado_id == supermercado.id,
            Precio.fecha == fecha,
        )
    )
    if fila is None:
        fila = Precio(producto_id=producto.id, supermercado_id=supermercado.id, fecha=fecha)
        sesion.add(fila)
    fila.precio = encontrado.precio
    fila.precio_regular = encontrado.precio_regular
    fila.nombre_en_tienda = encontrado.nombre
    fila.id_en_tienda = encontrado.id_tienda
    fila.url = encontrado.url
    return fila


def ultima_fecha(sesion: Session) -> date | None:
    return sesion.scalar(select(func.max(Precio.fecha)))


def precios_del_dia(sesion: Session, fecha: date) -> list[Precio]:
    return list(sesion.scalars(select(Precio).where(Precio.fecha == fecha)))


def historial(sesion: Session, codigo_producto: str) -> list[Precio]:
    consulta = (
        select(Precio)
        .join(Producto)
        .where(Producto.codigo == codigo_producto)
        .order_by(Precio.fecha)
    )
    return list(sesion.scalars(consulta))


def listar_productos(sesion: Session) -> list[Producto]:
    return list(sesion.scalars(select(Producto).order_by(Producto.categoria, Producto.nombre)))


def listar_supermercados(sesion: Session) -> list[Supermercado]:
    return list(sesion.scalars(select(Supermercado).order_by(Supermercado.nombre)))
