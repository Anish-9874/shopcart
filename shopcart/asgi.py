import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "shopcart.settings.prod",
)

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_application = get_asgi_application()

from apps.chat.routing import websocket_urlpatterns as chat_urlpatterns
from apps.notifications.routing import websocket_urlpatterns as notification_urlpatterns

# Combine websocket URL patterns from multiple apps
websocket_urlpatterns = chat_urlpatterns + notification_urlpatterns


application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
