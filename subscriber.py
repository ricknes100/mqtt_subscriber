import json
import ssl
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import MQTTConfig
from database import Database
from handlers import validar_valor, obtener_unidad
from laravel import LaravelBroadcast
from logger import get_logger

log = get_logger("subscriber")

class MQTTSubscriber:
    def __init__(self):
        self.db      = Database()
        self.laravel = LaravelBroadcast()
        self.client  = mqtt.Client(client_id=MQTTConfig.CLIENT_ID, clean_session=True)
        self._configurar_cliente()

    def _configurar_cliente(self):
        if MQTTConfig.USER:
            self.client.username_pw_set(MQTTConfig.USER, MQTTConfig.PASSWORD)

        # TLS para EMQX Cloud
        if MQTTConfig.USE_TLS:
            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
            log.info("TLS activado")

        self.client.on_connect    = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message    = self._on_message

        self.client.will_set(
            "casa/sistema/subscriber",
            payload="offline",
            qos=1,
            retain=True,
        )

    # ── Callbacks ────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        codigos = {
            0: "Conectado correctamente",
            1: "Versión de protocolo incorrecta",
            2: "Client ID rechazado",
            3: "Broker no disponible",
            4: "Usuario o contraseña incorrectos",
            5: "No autorizado",
        }
        if rc == 0:
            log.info(f"MQTT: {codigos[rc]}")

            # Suscribirse solo a los topics configurados
            topics = [(topic, 1) for topic in MQTTConfig.TOPICS]
            client.subscribe(topics)

            for topic in MQTTConfig.TOPICS:
                log.info(f"  → Suscrito a: {topic}")

            client.publish("casa/sistema/subscriber", "online", retain=True)
        else:
            log.error(f"MQTT: Error de conexión — {codigos.get(rc, rc)}")

    def _on_disconnect(self, client, userdata, rc):
        if rc == 0:
            log.info("Desconexión limpia")
        else:
            log.warning(f"Desconexión inesperada (rc={rc}). Reconectando...")

    def _on_message(self, client, userdata, msg):
        try:
            # El topic ya es exactamente casa/ubicacion/sensor
            partes = msg.topic.split("/")
            if len(partes) != 3:
                return

            _, ubicacion, sensor = partes

            payload = json.loads(msg.payload.decode("utf-8"))
            valor   = float(payload.get("valor", payload))

            log.info(f"Recibido: {ubicacion}/{sensor} = {valor}")

            if not validar_valor(sensor, valor):
                return

            unidad    = obtener_unidad(sensor)
            timestamp = datetime.now(timezone.utc).isoformat()

            self.db.insert_lectura(sensor, ubicacion, valor, unidad)

            self.laravel.notify(
                sensor=sensor,
                ubicacion=ubicacion,
                valor=valor,
                unidad=unidad,
                timestamp=timestamp,
            )

        except json.JSONDecodeError:
            log.error(f"Payload inválido en {msg.topic}: {msg.payload}")
        except ValueError as e:
            log.error(f"Valor no numérico en {msg.topic}: {e}")
        except Exception as e:
            log.error(f"Error inesperado en {msg.topic}: {e}")

    # ── Ciclo de vida ─────────────────────────────────────────

    def start(self):
        while True:
            try:
                log.info(f"Conectando a {MQTTConfig.HOST}:{MQTTConfig.PORT}...")
                self.client.connect(
                    MQTTConfig.HOST,
                    MQTTConfig.PORT,
                    keepalive=60,
                )
                self.client.loop_forever()
            except ConnectionRefusedError:
                log.error("Broker MQTT no disponible. Reintentando en 10s...")
                time.sleep(10)
            except Exception as e:
                log.error(f"Error en el loop MQTT: {e}. Reintentando en 10s...")
                time.sleep(10)