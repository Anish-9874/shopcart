import os

from .base import *

# ---------------------------------------------------------
# PRODUCTION SETTINGS
# ---------------------------------------------------------

DEBUG = False


# ---------------------------------------------------------
# ALLOWED HOSTS (RENDER + LOCAL TESTING)
# ---------------------------------------------------------

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ---------------------------------------------------------
# DATABASE ROUTER
# ---------------------------------------------------------

DATABASE_ROUTERS = [
    "shopcart.routers.ReplicaRouter",
]


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": config("PDB_ENGINE"),
        "NAME": config("PDB_NAME"),
        "USER": config("PDB_USER"),
        "PASSWORD": config("PDB_PASSWORD"),
        "HOST": config("PDB_HOST"),
        "PORT": config("PDB_PORT"),
    },
    "replica": {
        "ENGINE": config("RPDB_ENGINE"),
        "NAME": config("RPDB_NAME"),
        "USER": config("RPDB_USER"),
        "PASSWORD": config("RPDB_PASSWORD"),
        "HOST": config("RPDB_HOST"),
        "PORT": config("RPDB_PORT"),
    },
}


# ---------------------------------------------------------
# LOG DIRECTORY
# ---------------------------------------------------------

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": (
                "%(asctime)s "
                "%(levelname)s "
                "%(name)s "
                "%(message)s "
                "%(pathname)s "
                "%(lineno)d"
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "ERROR",
        },
        "rotating_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "timedebug.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": [
            "console",
            "rotating_file",
        ],
        "level": "INFO",
    },
    "loggers": {
        "django.request": {
            "handlers": [
                "console",
                "error_file",
            ],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": [
                "console",
                "rotating_file",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}
