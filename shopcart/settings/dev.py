from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE"),
        "NAME": BASE_DIR / config("DB_NAME"),
    }
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        #'rest_framework_simplejwt.authentication.JWTAuthentication'     #for enable JWT Authentication
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 8,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ShopCart API",
    "DESCRIPTION": "API documentation for ShopCart project",
    "VERSION": "1.0.0",
}


# for cache

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-cache",
    }
}


# CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

# CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"

# CELERY_TIMEZONE = "Asia/Kathmandu"
