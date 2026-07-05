# main.py
import sys

from subscriber import MQTTSubscriber
from logger import get_logger

log = get_logger("main")


if __name__ == "__main__":
    log.info("Iniciando subscriber MQTT para casa inteligente")

    sub = MQTTSubscriber()

    try:
        sub.start()
    except KeyboardInterrupt:
        log.info("Señal de interrupción recibida")
    finally:
        sub.client.publish("casa/sistema/subscriber", "offline", retain=True)
        sub.client.disconnect()
        log.info("Subscriber detenido correctamente")
        sys.exit(0)