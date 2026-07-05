import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import LaravelConfig
from logger import get_logger

log = get_logger("laravel")

class LaravelBroadcast:
    """
    Notifica a Laravel para que dispare el broadcast a Reverb.
    Usa reintentos automáticos con backoff exponencial.
    Si Laravel no está disponible, el dato ya está en BD — no es crítico.
    """

    def __init__(self):
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=1,                        # 1s, 2s, 4s
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://",  adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key":    LaravelConfig.API_KEY,
        })

        return session

    def notify(
        self,
        sensor:    str,
        ubicacion: str,
        valor:     float,
        unidad:    str,
        timestamp: str,
    ) -> None:
        """
        Envía los datos a Laravel para el broadcast WebSocket.
        No lanza excepciones — un fallo aquí no debe detener el subscriber.
        """
        payload = {
            "sensor":    sensor,
            "location":  ubicacion,
            "value":     valor,
            "unit":      unidad,
            "timestamp": timestamp,
        }

        try:
            response = self._session.post(
                LaravelConfig.URL,
                json=payload,
                timeout=LaravelConfig.TIMEOUT,
            )

            if response.status_code == 200:
                log.debug(
                    "📡 Broadcast OK → %s/%s = %s%s",
                    ubicacion, sensor, valor, unidad,
                )
            else:
                log.warning(
                    "Laravel retornó %s para %s/%s",
                    response.status_code, ubicacion, sensor,
                )

        except requests.exceptions.ConnectionError:
            log.warning("Laravel no disponible — broadcast omitido")
        except requests.exceptions.Timeout:
            log.warning("Timeout al notificar a Laravel")
        except Exception as e:
            log.warning("Error al notificar a Laravel: %s", e)