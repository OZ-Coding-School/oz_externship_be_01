import time
from typing import Any, Generator, Optional

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import permissions, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import ChatbotMessage, ChatbotSession, Question, QuestionAIAnswer
from ..serializers.ai_serializers import (
    ChatbotMessageSerializer,
    ChatbotSessionSerializer,
)


def mock_ai_stream(content: str) -> Generator[str, None, None]:
    chunks = [f"{content} (chunk {i+1})\n" for i in range(3)]
    for chunk in chunks:
        time.sleep(0.5)
        yield chunk


class ChatbotConnectAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> DRFResponse:
        token_user: Optional[Any] = request.user if request.user and request.user.is_authenticated else None
        question_id_raw = request.data.get("question_id")
        socket_id: str | None = request.data.get("socket_id")

        if not isinstance(question_id_raw, int):
            return DRFResponse({"detail": "올바르지 않은 질문 ID입니다."}, status=400)
        question_id = question_id_raw

        question = Question.objects.filter(id=question_id).first()
        if not question:
            return DRFResponse({"detail": "질문이 존재하지 않습니다."}, status=400)

        if token_user is None or not getattr(token_user, "is_staff", False):
            existing = ChatbotSession.objects.filter(user=token_user, question=question).order_by("-created_at").first()
            if existing and existing.chat_count >= 2:
                existing.status = "rejected"
                existing.rejection_reason = "최대 2회까지의 대화만 허용됩니다."
                existing.save()
                return DRFResponse({"detail": existing.rejection_reason}, status=403)

        session = ChatbotSession.objects.create(
            user=token_user, question=question, socket_id=socket_id or "", status="connected", chat_count=0
        )

        serializer = ChatbotSessionSerializer(session)
        return DRFResponse(serializer.data, status=200)


class ChatbotMessageAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> DRFResponse:
        session_id_raw = request.data.get("session_id")
        message_content: str | None = request.data.get("content")

        if not isinstance(session_id_raw, int):
            return DRFResponse({"detail": "올바르지 않은 세션 ID입니다."}, status=400)
        session_id = session_id_raw

        session = ChatbotSession.objects.filter(id=session_id, status="connected").first()
        if not session:
            return DRFResponse({"detail": "세션이 유효하지 않습니다."}, status=400)

        if session.is_waiting_reply:
            return DRFResponse({"detail": "AI 응답 대기 중입니다."}, status=429)

        is_related = message_content is not None and ("?" in message_content or len(message_content) > 10)

        ChatbotMessage.objects.create(
            session=session, sender_type="user", content=message_content or "", is_question_related=is_related
        )

        session.chat_count += 1
        session.is_waiting_reply = True
        session.save()

        ai_content = (
            f"'{message_content}'에 대한 답변입니다. (모의 응답)"
            if is_related
            else "죄송하지만, 질문과 관련된 내용만 답변드릴 수 있어요."
        )

        ChatbotMessage.objects.create(
            session=session, sender_type="ai", content=ai_content, is_question_related=is_related
        )

        session.is_waiting_reply = False
        session.save()

        return DRFResponse({"ai_response": ai_content, "chat_count": session.chat_count}, status=200)


class ChatbotDisconnectAPIView(APIView):
    def post(self, request: Request) -> DRFResponse:
        session_id_raw = request.data.get("session_id")
        if not isinstance(session_id_raw, int):
            return DRFResponse({"detail": "올바르지 않은 세션 ID입니다."}, status=400)
        session_id = session_id_raw

        session = ChatbotSession.objects.filter(id=session_id).first()
        if not session:
            return DRFResponse({"detail": "세션이 존재하지 않습니다."}, status=400)

        session.status = "disconnected"
        session.disconnected_at = timezone.now()
        session.save()

        return DRFResponse({"detail": "세션이 정상적으로 종료되었습니다."}, status=200)


class GenerateAIAnswerAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> StreamingHttpResponse:
        question_id_raw = request.data.get("question_id")
        if not isinstance(question_id_raw, int):
            return StreamingHttpResponse(mock_ai_stream("올바르지 않은 질문 ID입니다."), content_type="text/plain")
        question_id = question_id_raw

        question = Question.objects.filter(id=question_id).first()
        if not question:
            return StreamingHttpResponse(mock_ai_stream("질문이 존재하지 않습니다."), content_type="text/plain")

        existing_answer = QuestionAIAnswer.objects.filter(question=question).first()
        if existing_answer:
            return StreamingHttpResponse(mock_ai_stream(existing_answer.content), content_type="text/plain")

        ai_content = f"'{question.title}'에 대한 AI 모의 답변입니다."

        QuestionAIAnswer.objects.create(question=question, content=ai_content)

        return StreamingHttpResponse(mock_ai_stream(ai_content), content_type="text/plain")


class AIPromptChatAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request: Request) -> StreamingHttpResponse | DRFResponse:
        question_id_raw = request.data.get("question_id")
        message: str | None = request.data.get("message")
        user: Optional[Any] = request.user if request.user and request.user.is_authenticated else None

        if not isinstance(question_id_raw, int):
            return DRFResponse({"detail": "올바르지 않은 질문 ID입니다."}, status=400)
        question_id = question_id_raw

        question = Question.objects.filter(id=question_id).first()
        if not question:
            return DRFResponse({"detail": "질문이 존재하지 않습니다."}, status=400)

        session, _ = ChatbotSession.objects.get_or_create(
            user=user,
            question=question,
            defaults={"socket_id": "ai-prompt", "status": "connected", "chat_count": 0, "is_waiting_reply": False},
        )

        is_privileged = False
        if user and getattr(user, "is_staff", False):
            is_privileged = True
        elif user and hasattr(user, "groups"):
            is_privileged = user.groups.filter(name__in=["수강생", "스태프", "관리자"]).exists()

        if not is_privileged and session.chat_count >= 2:
            ChatbotMessage.objects.create(
                session=session,
                sender_type="ai",
                content="AI 챗봇은 2회까지만 사용 가능합니다. 수강 등록 후 이용해 주세요.",
                is_question_related=True,
            )
            return DRFResponse({"detail": "비회원은 2회까지만 이용 가능합니다.", "chat_disabled": True}, status=403)

        ChatbotMessage.objects.create(
            session=session, sender_type="user", content=message or "", is_question_related=True
        )

        ai_response = f"'{message}'에 대한 AI 모의 응답입니다."

        ChatbotMessage.objects.create(session=session, sender_type="ai", content=ai_response, is_question_related=True)

        session.chat_count += 1
        session.save()

        return StreamingHttpResponse(mock_ai_stream(ai_response), content_type="text/plain")
