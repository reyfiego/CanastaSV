"""Definición de las tablas de la base de datos."""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Supermercado(Base):
    __tablename__ = "supermercados"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True)
    nombre: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(255))


class Producto(Base):
    """Producto canónico de la canasta (el mismo para todos los supermercados)."""

    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True)
    nombre: Mapped[str] = mapped_column(String(120))
    categoria: Mapped[str] = mapped_column(String(80))
    tamano_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    tamano_unidad: Mapped[str | None] = mapped_column(String(10), nullable=True)

    precios: Mapped[list["Precio"]] = relationship(back_populates="producto")


class Precio(Base):
    """Un precio observado: un producto, en un supermercado, en un día."""

    __tablename__ = "precios"
    __table_args__ = (UniqueConstraint("producto_id", "supermercado_id", "fecha"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    supermercado_id: Mapped[int] = mapped_column(ForeignKey("supermercados.id"))
    fecha: Mapped[date] = mapped_column(Date, index=True)
    precio: Mapped[float] = mapped_column(Float)
    precio_regular: Mapped[float | None] = mapped_column(Float, nullable=True)
    nombre_en_tienda: Mapped[str] = mapped_column(String(255))
    id_en_tienda: Mapped[str] = mapped_column(String(80))
    url: Mapped[str] = mapped_column(String(500))
    capturado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    producto: Mapped[Producto] = relationship(back_populates="precios")
    supermercado: Mapped[Supermercado] = relationship()
