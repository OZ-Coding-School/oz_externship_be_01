import json
import os

import httpx
from channels.generic.websocket import AsyncWebsocketConsumer  # type: ignore

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        # 1. 사용자 유형 판별
        user = self.scope.get("user")
        user_type = getattr(user, "role", "guest")  # ADMIN, GENERAL, STUDENT, TA, OM, LC

        # 2. 인사말 및 메뉴 버튼 전송
        await self.send(
            text_data=json.dumps(
                {
                    "type": "greeting",
                    "message": "What's Up, Dickie?",
                    "menu": [{"id": "guide", "label": "홈페이지 사용법"}, {"id": "ai", "label": "AI 질문하기"}],
                }
            )
        )
        # 이후 receive에서 메뉴 선택 처리

    async def receive(self, text_data):
        data = json.loads(text_data)
        menu_id = data.get("menu_id")
        action = data.get("action")
        user = self.scope.get("user")
        user_type = getattr(user, "role", "guest")

        # 3. 홈페이지 사용법 메뉴 선택 시 계정별 세부 메뉴 분기
        if menu_id == "guide":
            if user_type in ["TA", "OM", "LC", "ADMIN"]:
                submenu = [
                    {"id": "terms", "label": "이용 약관 확인"},
                    {"id": "auth", "label": "회원가입 및 로그인"},
                    {"id": "community", "label": "커뮤니티"},
                    {"id": "qna", "label": "질의응답"},
                    {"id": "assignment", "label": "과제"},
                    {"id": "quiz", "label": "쪽지시험"},
                ]
            elif user_type == "STUDENT":
                submenu = [
                    {"id": "terms", "label": "이용 약관 확인"},
                    {"id": "auth", "label": "회원가입 및 로그인"},
                    {"id": "community", "label": "커뮤니티"},
                    {"id": "qna", "label": "질의응답"},
                    {"id": "assignment", "label": "과제"},
                    {"id": "quiz", "label": "쪽지시험"},
                ]
            else:  # 일반 회원, 비회원 등
                submenu = [
                    {"id": "terms", "label": "이용 약관 확인"},
                    {"id": "auth", "label": "회원가입 및 로그인"},
                    {"id": "community", "label": "커뮤니티"},
                ]
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "submenu",
                        "menu": submenu,
                    }
                )
            )

        # 3. AI 질문하기 메뉴 선택 시 안내 메시지 전송
        elif menu_id == "ai":
            await self.send(
                text_data=json.dumps(
                    {"type": "ai_intro", "message": "대화를 시작할 수 있습니다! 궁금한 것들을 질문해보세요!"}
                )
            )

        # ✅ -> 사용자가 실제 질문을 보낼 때 (예: action == "ai_question")
        elif action == "ai_question":
            user_message = data.get("message")
            async for char in self.ask_gemini_stream(user_message):
                await self.send(text_data=json.dumps({"type": "ai_stream", "message": char}, ensure_ascii=False))

        # 4. 세부 메뉴 선택 등 추가 분기 처리(예시)
        elif action == "select_submenu":
            submenu_id = data.get("submenu_id")
            if submenu_id == "terms":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "이용 약관 확인",
                            "message": "서비스 이용 약관을 확인할 수 있습니다.",
                            "image_url": "/static/images/terms.png",
                        }
                    )
                )
            elif submenu_id == "auth":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "회원가입 및 로그인",
                            "message": "회원가입과 로그인 방법을 안내합니다.",
                            "image_url": "/static/images/auth.png",
                        }
                    )
                )
            elif submenu_id == "community":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "커뮤니티",
                            "message": "커뮤니티 게시판을 통해 다양한 정보를 공유하세요.",
                            "image_url": "/static/images/community.png",
                        }
                    )
                )
            elif submenu_id == "qna":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "질의응답",
                            "message": "질의응답 게시판에서 질문하고 답변을 받을 수 있습니다.",
                            "image_url": "/static/images/qna.png",
                        }
                    )
                )
            elif submenu_id == "assignment":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "과제",
                            "message": "과제 제출 및 확인 방법을 안내합니다.",
                            "image_url": "/static/images/assignment.png",
                        }
                    )
                )
            elif submenu_id == "quiz":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "쪽지시험",
                            "message": "쪽지시험 응시 및 결과 확인 방법을 안내합니다.",
                            "image_url": "/static/images/quiz.png",
                        }
                    )
                )
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "info",
                            "title": "알 수 없는 메뉴",
                            "message": "선택하신 메뉴에 대한 정보를 찾을 수 없습니다.",
                        }
                    )
                )

    # Gemini API에 질문을 보내고, 응답을 스트리밍(한 토큰/문장씩) yield
    async def ask_gemini_stream(self, prompt):
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        async with httpx.AsyncClient(timeout=60.0) as client:
            # 전체 응답을 받아 한 글자씩
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

            # 답변 추출
            gemini_message = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "죄송합니다. 답변을 생성하지 못했습니다.")
            )
            # 한 글자씩 스트리밍 전송
            for char in gemini_message:
                yield char

    async def disconnect(self, close_code):
        # 예시: 그룹에서 제거, 로그 기록, 세션 정리 등
        # await self.channel_layer.group_discard("room_name", self.channel_name)
        print(f"WebSocket disconnected: {close_code}")
