"""Creación del motor y las sesiones de base de datos."""

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from canastasv.db.tablas import Base

# FastAPI atiende peticiones en varios hilos; SQLite lo permite con esta opción.
_OPCIONES_SQLITE = {"check_same_thread": False}


def crear_motor(ruta_db: Path | str) -> Engine:
    """Crea el motor SQLite. Usa ':memory:' para pruebas."""
    if str(ruta_db) == ":memory:":
        return create_engine("sqlite://", connect_args=_OPCIONES_SQLITE, poolclass=StaticPool)
    ruta = Path(ruta_db)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{ruta}", connect_args=_OPCIONES_SQLITE)


def inicializar(motor: Engine) -> None:
    Base.metadata.create_all(motor)


def fabrica_de_sesiones(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=motor, expire_on_commit=False)
