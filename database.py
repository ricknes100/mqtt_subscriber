import psycopg2
import psycopg2.extras
from config import DBConfig
from logger import get_logger

log = get_logger("database")

class Database:
    def __init__(self):
        self._conn = None
        self._connect()

    def _connect(self):
        """Establece la conexión con reintentos."""
        self._conn = psycopg2.connect(
            host=DBConfig.HOST,
            port=DBConfig.PORT,
            dbname=DBConfig.NAME,
            user=DBConfig.USER,
            password=DBConfig.PASSWORD,
            connect_timeout=10,
        )
        self._conn.autocommit = True
        log.info("Conexión a PostgreSQL establecida")

    def _ensure_connection(self):
        """Reconecta si la conexión se perdió."""
        try:
            self._conn.isolation_level  # ping ligero
        except Exception:
            log.warning("Conexión perdida, reconectando...")
            self._connect()

    def insert_lectura(self, sensor: str, ubicacion: str, valor: float, unidad: str):
        """Inserta una lectura de sensor en la tabla de series de tiempo."""
        self._ensure_connection()
        try:
            with self._conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO readings (timestamp, sensor, location, value, unit)
                    VALUES (NOW(), %s, %s, %s, %s)
                """, (sensor, ubicacion, valor, unidad))
            log.debug(f"Guardado: {ubicacion}/{sensor} = {valor} {unidad}")
        except Exception as e:
            log.error(f"Error al insertar lectura: {e}")
            raise
