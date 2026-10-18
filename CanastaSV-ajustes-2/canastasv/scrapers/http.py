"""Cliente HTTP compartido: reintentos, tiempo de espera y pausa entre peticiones."""

import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from canastasv.config import Ajustes

CARACTERES_DE_DETALLE = 200


class ErrorDeDescarga(RuntimeError):
    """Se lanza cuando una página no se pudo descargar tras los reintentos."""


class ClienteHttp:
    """Envuelve requests.Session para ser respetuosos con los sitios consultados."""

    def __init__(self, ajustes: Ajustes):
        self._ajustes = ajustes
        self._ultima_peticion = 0.0
        self._sesion = requests.Session()
        self._sesion.headers.update({"User-Agent": ajustes.user_agent, "Accept": "application/json, text/html"})
        reintentos = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        self._sesion.mount("https://", HTTPAdapter(max_retries=reintentos))

    def _esperar_turno(self) -> None:
        transcurrido = time.monotonic() - self._ultima_peticion
        pendiente = self._ajustes.espera_entre_peticiones - transcurrido
        if pendiente > 0:
            time.sleep(pendiente)
        self._ultima_peticion = time.monotonic()

    def get(self, url: str, params: dict | None = None) -> requests.Response:
        self._esperar_turno()
        try:
            respuesta = self._sesion.get(url, params=params, timeout=self._ajustes.timeout)
        except requests.RequestException as error:
            raise ErrorDeDescarga(f"No se pudo conectar con {url}: {error}") from error
        if not respuesta.ok:
            # Se incluye el inicio de la respuesta: suele explicar por qué el servidor la rechazó.
            detalle = " ".join(respuesta.text[:CARACTERES_DE_DETALLE].split())
            raise ErrorDeDescarga(f"{respuesta.status_code} en {respuesta.url} — {detalle}")
        return respuesta
