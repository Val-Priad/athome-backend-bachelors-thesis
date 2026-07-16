import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask

LOG_FOLDER = Path(__file__).resolve().parent
_HANDLER_MARKER = "athome_application_handler"


def setup_logging(app: Flask) -> None:
    LOG_FOLDER.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(app.config.get("LOG_LEVEL", logging.INFO))

    if any(
        getattr(handler, _HANDLER_MARKER, False)
        for handler in root_logger.handlers
    ):
        return

    file_handler = RotatingFileHandler(
        f"{LOG_FOLDER}/log.log",
        maxBytes=5 * 1024 * 1024,
        encoding="utf-8",
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    setattr(file_handler, _HANDLER_MARKER, True)
    setattr(stream_handler, _HANDLER_MARKER, True)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
