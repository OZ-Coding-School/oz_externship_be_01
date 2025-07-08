from urllib.parse import parse_qs

import jwt
from channels.middleware import BaseMiddleware  # type: ignore
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token_list = parse_qs(query_string).get("token")
        if not token_list:
            await self.close_with_code(send, 4001, "인증 토큰 누락")
            return
        token = token_list[0]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # 토큰 타입 체크 (access 토큰만 허용)
            if payload.get("type") != "access":
                await self.close_with_code(send, 4004, "잘못된 토큰 타입")
                return

            # 유저 조회 부분 주석 처리 (임시로 무조건 인증 성공 처리)
            # user_id = payload.get("user_id")
            # user = await get_user(user_id)
            # if user is None:
            #     await self.close_with_code(send, 4003, "유효하지 않은 사용자")
            #     return
            # scope["user"] = user

            # 대신 scope에 임의의 익명 유저 객체 넣기 (optional)
            scope["user"] = "anonymous"  # 혹은 그냥 payload 넣어도 됨

        except ExpiredSignatureError:
            await self.close_with_code(send, 4002, "토큰 만료")
            return
        except InvalidTokenError:
            await self.close_with_code(send, 4004, "유효하지 않은 토큰")
            return

        return await super().__call__(scope, receive, send)

    async def close_with_code(self, send, code, reason):
        await send(
            {
                "type": "websocket.close",
                "code": code,
                "reason": reason,
            }
        )
