from urllib.parse import parse_qs

import jwt
from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware  # type: ignore
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


@sync_to_async
def get_user(user_id):
    try:
        return get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token")

        if not token:
            # 비로그인 사용자: 익명 사용자로 처리
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        try:
            payload = jwt.decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("token_type") != "access":
                await self.close_connection(send, 4004, "잘못된 토큰 타입")
                return

            user_id = payload.get("user_id")
            user = await get_user(user_id)
            if user is None:
                await self.close_connection(send, 4003, "사용자를 찾을 수 없음")
                return

            scope["user"] = user

        except ExpiredSignatureError:
            await self.close_connection(send, 4001, "토큰이 만료되었습니다")
            return
        except InvalidTokenError:
            await self.close_connection(send, 4002, "유효하지 않은 토큰입니다")
            return

        return await super().__call__(scope, receive, send)

    async def close_connection(self, send, code, message):
        await send({"type": "websocket.close", "code": code, "text": message})
