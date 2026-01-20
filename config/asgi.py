import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()  # 🔥 ESTO ES CLAVE

from chat_messages.routing import websocket_urlpatterns
from common.middleware import JWTAuthMiddleware  # ← AHORA SÍ

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
