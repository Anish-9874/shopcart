from .base import *

DEBUG = False


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


DATABASES = {
    "default": {
        "ENGINE": config("PDB_ENGINE"),
        "NAME": config("PDB_NAME"),
        "USER": config("PDB_USER"),
        "PASSWORD": config("PDB_PASSWORD"),
        "HOST": config("PDB_HOST"),
        "PORT": config("PDB_PORT"),
    }
}


# ---------------------------------------------------------
# LOG DIRECTORY
# ---------------------------------------------------------

LOG_DIR = BASE_DIR / "logs"

# Create logs/ directory automatically if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------

LOGGING = {
    "version": 1,
    # Keep Django's existing loggers active
    "disable_existing_loggers": False,
    # -----------------------------------------------------
    # FORMATTERS
    # -----------------------------------------------------
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
    # -----------------------------------------------------
    # HANDLERS
    # -----------------------------------------------------
    "handlers": {
        # ---------------------------------------------
        # Console Handler
        # ---------------------------------------------
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "ERROR",
        },
        #  "try_It": {
        #             "class": "logging.FileHandler",
        #             "filename" : LOG_DIR / "hello.log",
        #             "formatter": "json",
        #             "level" : "ERROR",
        # },
        # ---------------------------------------------
        # General Log File
        # 5 MB per file
        # 3 backup files
        # ---------------------------------------------
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "debug.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
        # ---------------------------------------------
        # General Log File
        # rotate daily midnight
        # 3 backup files
        # ---------------------------------------------
        "rotating_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_DIR / "timedebug.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
        # ---------------------------------------------
        # Error Log File
        # 5 MB per file
        # 3 backup files
        # ---------------------------------------------
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
    },
    # -----------------------------------------------------
    # ROOT LOGGER
    # -----------------------------------------------------
    "root": {
        "handlers": [
            "console",
            "rotating_file",
        ],
        "level": "INFO",
    },
    # -----------------------------------------------------
    # SPECIFIC LOGGERS
    # -----------------------------------------------------
    "loggers": {
        # ---------------------------------------------
        # Django Request Errors
        # ---------------------------------------------
        "django.request": {
            "handlers": [
                "console",
                "error_file",
            ],
            "level": "ERROR",
            "propagate": False,
        },
        # # ---------------------------------------------
        # # Django Server Logs
        # # ---------------------------------------------
        # "django.server": {
        #     "handlers": [
        #         "console",
        #         "rotating_file",
        #     ],
        #     "level": "INFO",
        #     "propagate": False,
        # },
        # # ---------------------------------------------
        # # Database Logs
        # # ---------------------------------------------
        # "django.db.backends": {
        #     "handlers": [
        #         "console",
        #         "rotating_file",
        #     ],
        #     "level": "WARNING",
        #     "propagate": False,
        # },
        # ---------------------------------------------
        # Your Application Logs
        # ---------------------------------------------
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
