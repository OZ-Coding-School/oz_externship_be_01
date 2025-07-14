import json
import os

import httpx
from channels.db import database_sync_to_async  # type: ignore
from channels.generic.websocket import AsyncWebsocketConsumer  # type: ignore
from apps.qna.utils.redis import get_ai_count, increment_ai_count

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.user = self.scope.get("user")
        self.session = self.scope.get("session")
        self.session_key = self.session.session_key or "anonymous"

        # 인사말 및 기본 메뉴 전송
        await self.send(
            text_data=json.dumps(
                {
                    "type": "greeting",
                    "message": "What's Up, Dickie?",
                    "menu": [{"id": "guide", "label": "홈페이지 사용법"}, {"id": "ai", "label": "AI 질문하기"}],
                }
            )
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        menu_id = data.get("menu_id")
        action = data.get("action")
        user_message = data.get("message")

        user = self.scope.get("user")
        session_key = self.session_key
        user_type = getattr(user, "role", "guest")

        # 홈페이지 사용법 메뉴
        if menu_id == "guide":
            if user_type in ["TA", "OM", "LC", "ADMIN", "STUDENT"]:
                submenu = [
                    {"id": "terms", "label": "이용 약관 확인"},
                    {"id": "auth", "label": "회원가입 및 로그인"},
                    {"id": "community", "label": "커뮤니티"},
                    {"id": "qna", "label": "질의응답"},
                    {"id": "assignment", "label": "과제"},
                    {"id": "quiz", "label": "쪽지시험"},
                ]
            else:
                submenu = [
                    {"id": "terms", "label": "이용 약관 확인"},
                    {"id": "auth", "label": "회원가입 및 로그인"},
                    {"id": "community", "label": "커뮤니티"},
                ]
            await self.send(text_data=json.dumps({"type": "submenu", "menu": submenu}))

        # AI 질문 메뉴 선택
        elif menu_id == "ai":
            await self.send(
                text_data=json.dumps(
                    {"type": "ai_intro", "message": "대화를 시작할 수 있습니다! 궁금한 것들을 질문해보세요!"}
                )
            )

        # AI 질문 실행
        elif action == "ai_question":
            is_limited_user = not user.is_authenticated or getattr(user, "role", "GENERAL") == "GENERAL"

            if is_limited_user:
                count = await self.get_ai_count_async(session_key)
                if count >= 2:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "limit",
                                "message": "비회원 및 일반 유저는 AI와 최대 2회까지만 대화할 수 있습니다.",
                            }
                        )
                    )
                    return
                await self.increment_ai_count_async(session_key)

            # 질문을 보낸 직후 입력 잠금 신호 전송
            await self.send(text_data=json.dumps({"type": "input_lock", "status": True}))

            # 질문 무관 메시지 필터링 (조건은 같지만 입력 잠금 해제 추가)
            if not self.is_relevant(user_message):
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "irrelevant",
                            "message": "질문과 관련된 내용만 답변할 수 있습니다.",
                            "input_lock": False,  # 입력창 다시 활성화
                        }
                    )
                )
                return

            # Gemini 응답 스트리밍
            async for char in self.ask_gemini_stream(user_message):
                await self.send(text_data=json.dumps({"type": "ai_stream", "message": char}, ensure_ascii=False))

            # 응답 끝난 뒤 입력창 다시 활성화
            await self.send(text_data=json.dumps({"type": "input_lock", "status": False}))

        # 세부 서브 메뉴 안내
        elif action == "select_submenu":
            submenu_id = data.get("submenu_id")
            await self.send(text_data=json.dumps(self.get_submenu_response(submenu_id)))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("room_name", self.channel_name)

    # Gemini API 요청
    async def ask_gemini_stream(self, prompt):
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

            gemini_message = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "죄송합니다. 답변을 생성하지 못했습니다.")
            )

            for char in gemini_message:
                yield char

    # Redis 연동
    @database_sync_to_async
    def get_ai_count_async(self, session_key):
        return get_ai_count(session_key)

    @database_sync_to_async
    def increment_ai_count_async(self, session_key):
        return increment_ai_count(session_key)

    # 질문 무관 메시지 필터링
    def is_relevant(self, message):
        banned = ["ㅋㅋ", "ㅎㅇ", "뭐해", "바보", "욕설"]
        if not message or len(message) < 5:
            return False
        if any(bad in message for bad in banned):
            return False
        return True

    # 서브 메뉴 응답 생성기
    def get_submenu_response(self, submenu_id):
        submenu_data = {
            "terms": {
                "title": "이용 약관 확인",
                "message": "서비스 이용 약관을 확인할 수 있습니다.",
                "image_url": "/static/images/terms.png",
            },
            "auth": {
                "title": "회원가입 및 로그인",
                "message": "회원가입과 로그인 방법을 안내합니다.",
                "image_url": "/static/images/auth.png",
            },
            "community": {
                "title": "커뮤니티",
                "message": "커뮤니티 게시판을 통해 다양한 정보를 공유하세요.",
                "image_url": "/static/images/community.png",
            },
            "qna": {
                "title": "질의응답",
                "message": "질의응답 게시판에서 질문하고 답변을 받을 수 있습니다.",
                "image_url": "/static/images/qna.png",
            },
            "assignment": {
                "title": "과제",
                "message": "과제 제출 및 확인 방법을 안내합니다.",
                "image_url": "/static/images/assignment.png",
            },
            "quiz": {
                "title": "쪽지시험",
                "message": "쪽지시험 응시 및 결과 확인 방법을 안내합니다.",
                "image_url": "/static/images/quiz.png",
            },
        }
        return {
            "type": "info",
            **submenu_data.get(
                submenu_id,
                {
                    "title": "알 수 없는 메뉴",
                    "message": "선택하신 메뉴에 대한 정보를 찾을 수 없습니다.",
                },
            ),
        }
