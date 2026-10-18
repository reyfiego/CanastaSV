"""Configuración central del proyecto, leída desde variables de entorno (.env)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
DIR_CONFIG = RAIZ_PROYECTO / "config"

load_dotenv(RAIZ_PROYECTO / ".env")


@dataclass(frozen=True)
class Ajustes:
    ruta_db: Path
    espera_entre_peticiones: float
    timeout: float
    user_agent: str


def _leer_float(nombre: str, por_defecto: float) -> float:
    valor = os.getenv(nombre)
    if valor is None or valor.strip() == "":
        return por_defecto
    try:
        return float(valor)
    except ValueError as error:
        raise ValueError(f"La variable {nombre} debe ser un número, se recibió: {valor!r}") from error


def cargar_ajustes() -> Ajustes:
    ruta_db = Path(os.getenv("CANASTASV_DB", "data/canastasv.db"))
    if not ruta_db.is_absolute():
        ruta_db = RAIZ_PROYECTO / ruta_db
    return Ajustes(
        ruta_db=ruta_db,
        espera_entre_peticiones=_leer_float("CANASTASV_DELAY", 1.5),
        timeout=_leer_float("CANASTASV_TIMEOUT", 20.0),
        user_agent=(
            "CanastaSV/0.1 (proyecto académico de comparación de precios; "
            "+https://github.com/reyfiego/CanastaSV)"
        ),
    )
