import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from chat_messages.routing import websocket_urlpatterns as chat_ws
from users.routing import websocket_urlpatterns as users_ws
from rooms.routing import websocket_urlpatterns as rooms_ws
from common.middleware import JWTAuthMiddleware

from channels.routing import URLRouter
from itertools import chain

# Combinar todos los websockets en un solo URLRouter
all_websocket_patterns = list(chain(chat_ws, users_ws, rooms_ws))

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(all_websocket_patterns)),
    }
)
