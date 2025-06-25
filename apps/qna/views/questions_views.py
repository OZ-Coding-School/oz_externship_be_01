from types import SimpleNamespace
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ...users.models import User
from ..models import Question, QuestionCategory
from ..serializers.questions_serializers import (
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateSerializer,
)

# --- Mock Dummy Data ---
DUMMY_QUESTIONS = [
    Question(
        id=i,
        title=f"샘플 질문 제목 {i}",
        content=f"샘플 질문 내용 {i}",
        author=User(id=1, nickname="oz_student"),  # 실제 저장 X, 메모리 객체
        category=QuestionCategory(id=3, name="오류"),  # 마찬가지
    )
    for i in range(1, 4)
]


# 1. 질문 목록 조회 (GET)
class QuestionListView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=QuestionListSerializer(many=True),
        description="질문 리스트 조회",
        tags=["questions"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = QuestionListSerializer(DUMMY_QUESTIONS, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 2. 질문 상세 조회 (GET)
class QuestionDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=QuestionDetailSerializer,
        description="질문 상세 조회",
        tags=["questions"],
    )
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        item = next((q for q in DUMMY_QUESTIONS if q.id == question_id), None)
        if not item:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 3. 새 질문 생성 (POST)
class QuestionCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionDetailSerializer,
        description="새 질문 생성",
        tags=["questions"],
    )
    def post(self, request: Request) -> Response:
        serializer = QuestionCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


# 4. 질문 부분 수정 (PATCH)
class QuestionUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=QuestionUpdateSerializer,
        responses=QuestionDetailSerializer,
        description="질문 부분 수정",
        tags=["questions"],
    )
    def patch(self, request: Request, question_id: int) -> Response:
        payload = {**request.data, "id": question_id}
        serializer = QuestionUpdateSerializer(data=payload, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
