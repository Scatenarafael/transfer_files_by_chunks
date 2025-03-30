# -*- coding: utf-8 -*-
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    os.makedirs("logs")
except OSError:
    pass

logs = {
    "conections": os.path.join(BASE_DIR, "logs/conections.log"),
    "error": os.path.join(BASE_DIR, "logs/error.log"),
    "celery": os.path.join(BASE_DIR, "logs/celery.log"),
}

for key in logs:
    log_file = Path(logs[key])
    if not os.path.exists(log_file):
        open(log_file, "w").close()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S",
        },
    },
    "handlers": {
        "conections": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs["conections"],
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "simple",
        },
        "celery": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs["celery"],
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "simple",
        },
    },
    "loggers": {
        "conections_logger": {
            "handlers": ["conections"],
            "level": "DEBUG",
            "propagate": True,
        },
        "celery": {
            "handlers": ["celery"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
