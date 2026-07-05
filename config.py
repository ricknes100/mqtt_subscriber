from dotenv import load_dotenv
import os

load_dotenv()

class MQTTConfig:
    HOST      = os.getenv("MQTT_HOST", "localhost")
    PORT      = int(os.getenv("MQTT_PORT", 8883))
    USER      = os.getenv("MQTT_USER", "")
    PASSWORD  = os.getenv("MQTT_PASSWORD", "")
    CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "smarthome_subscriber")
    USE_TLS = os.getenv("MQTT_USE_TLS", "true").lower() == "true"
    TOPICS = [
        "casa/cocina/temperatura",
        "casa/cocina/humedad",
        "casa/cocina/gas",
        "casa/terraza/lluvia",
        "casa/garaje/puerta",
    ]

class DBConfig:
    HOST     = os.getenv("DB_HOST", "localhost")
    PORT     = int(os.getenv("DB_PORT", 5432))
    NAME     = os.getenv("DB_NAME", "smarthome")
    USER     = os.getenv("DB_USER", "postgres")
    PASSWORD = os.getenv("DB_PASSWORD", "")

class LaravelConfig:
    URL     = os.getenv("LARAVEL_URL", "http://localhost:8000/api/broadcast")
    API_KEY = os.getenv("LARAVEL_API_KEY", "")
    TIMEOUT = int(os.getenv("LARAVEL_TIMEOUT", 3))