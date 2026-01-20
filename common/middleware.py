from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async

User = get_user_model()


@database_sync_to_async
def get_user(token):
    try:
        validated = JWTAuthentication().get_validated_token(token)
        return JWTAuthentication().get_user(validated)
    except Exception as e:
        print("JWT ERROR:", e)
        return None


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        print("WS QUERY:", scope["query_string"])
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        token = params.get("token")
        if token:
            scope["user"] = await get_user(token[0])
        else:
            scope["user"] = None

        return await self.app(scope, receive, send)
