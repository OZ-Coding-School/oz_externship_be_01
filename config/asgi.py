import os

from django.core.asgi import get_asgi_application

# 환경변수 설정 -> base
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# django ASGI application 초기화
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from apps.qna import routing
from apps.qna.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
    }
)
