# handlers.py
from logger import get_logger

log = get_logger("handlers")

SENSOR_CONFIG: dict[str, dict] = {
    "temperatura": {"min": -10,  "max": 60,   "unidad": "°C"},
    "humedad":     {"min": 0,    "max": 100,  "unidad": "%"},
    "gas":         {"min": 0,    "max": 1023, "unidad": "ppm"},
    "lluvia":      {"min": 0,    "max": 1,    "unidad": "bool"},
    "luz":         {"min": 0,    "max": 4095, "unidad": "lux"},
    "lector":      {"min": None, "max": None, "unidad": "id"},
}

def validar_valor(sensor: str, valor: float) -> bool:
    """
    Verifica que el valor esté dentro del rango válido del sensor.
    Retorna True si es válido, False si debe descartarse.
    """
    config = SENSOR_CONFIG.get(sensor)

    if not config:
        log.debug("Sensor '%s' sin config de rango — se acepta", sensor)
        return True

    minv, maxv = config["min"], config["max"]

    if minv is not None and valor < minv:
        log.warning(
            "Fuera de rango: %s=%s (mín: %s) — descartado",
            sensor, valor, minv,
        )
        return False

    if maxv is not None and valor > maxv:
        log.warning(
            "Fuera de rango: %s=%s (máx: %s) — descartado",
            sensor, valor, maxv,
        )
        return False

    return True

def obtener_unidad(sensor: str) -> str:
    return SENSOR_CONFIG.get(sensor, {}).get("unidad", "")