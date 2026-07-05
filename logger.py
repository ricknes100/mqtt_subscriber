# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Consola — forzar utf-8 en Windows
    console_handler = logging.StreamHandler()
    console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Archivo rotativo — utf-8 explícito
    file_handler = RotatingFileHandler(
        "subscriber.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",      # ← esto resuelve el error
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger