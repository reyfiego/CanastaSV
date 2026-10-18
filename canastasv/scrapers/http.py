"""Cliente HTTP compartido: reintentos, tiempo de espera y pausa entre peticiones."""

import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from canastasv.config import Ajustes


class ErrorDeDescarga(RuntimeError):
    """Se lanza cuando una página no se pudo descargar tras los reintentos."""


class ClienteHttp:
    """Envuelve requests.Session para ser respetuosos con los sitios consultados."""

    def __init__(self, ajustes: Ajustes):
        self._ajustes = ajustes
        self._ultima_peticion = 0.0
        self._sesion = requests.Session()
        self._sesion.headers.update(
            {"User-Agent": ajustes.user_agent, "Accept-Language": "es-SV,es;q=0.9"}
        )
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
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ErrorDeDescarga(f"No se pudo descargar {url}: {error}") from error
        return respuesta
