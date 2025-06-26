from datetime import datetime

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.models import Answer, AnswerImage, Question, QuestionCategory
from apps.qna.serializers.answers_serializers import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerListSerializer,
    AnswerUpdateSerializer,
)
from apps.users.models import User


class AnswerCreateView(APIView):
    serializer_class = AnswerCreateSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerCreateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 생성",
        tags=["answer"],
    )
    def post(self, request: Request, question_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        dummy_question = Question(
            id=question_id,
            title="더미 질문 제목",
            content="더미 질문 내용",
            author=User(id=1, nickname="oz_student"),
            category=QuestionCategory(id=2, name="더미"),
        )

        dummy_answer = Answer(
            id=456,
            question=dummy_question,
            author=User(id=2, nickname="oz_coach", profile_image_url="/media/profile.png"),
            content=serializer.validated_data.get("content"),
            is_adopted=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        dummy_answer_images = [
            AnswerImage(
                id=i,
                answer=dummy_answer,
                img_url=f"/media/{image.name}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i, image in enumerate(serializer.validated_data["image_files"])
        ]

        response_data = AnswerListSerializer(dummy_answer).data
        response_data["image_urls"] = [image.img_url for image in dummy_answer_images]
        return Response(response_data, status=status.HTTP_201_CREATED)


class AnswerUpdateView(APIView):
    serializer_class = AnswerUpdateSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=AnswerUpdateSerializer,
        responses=AnswerListSerializer,
        description="질문에 대한 답변 수정",
        tags=["answer"],
    )
    def put(self, request: Request, question_id: int, answer_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        dummy_question = Question(
            id=question_id,
            title="더미 질문 제목",
            content="더미 질문 내용",
            author=User(id=1, nickname="oz_student"),
            category=QuestionCategory(id=2, name="더미"),
        )

        dummy_answer = Answer(
            id=456,
            question=dummy_question,
            author=User(id=2, nickname="oz_coach", profile_image_url="/media/profile.png"),
            content=serializer.validated_data.get("content", "수정 전"),
            is_adopted=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        dummy_answer_images = [
            AnswerImage(
                id=i,
                answer=dummy_answer,
                img_url=f"/media/{image.name}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i, image in enumerate(serializer.validated_data["image_files"])
        ]

        response_data = AnswerListSerializer(dummy_answer).data
        response_data["image_urls"] = [image.img_url for image in dummy_answer_images]
        return Response(response_data, status=status.HTTP_200_OK)


class AdoptAnswerView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description="답변 채택",
        tags=["answer"],
        parameters=[
            OpenApiParameter(name="question_id", type=int, location=OpenApiParameter.PATH, description="질문 ID"),
            OpenApiParameter(name="answer_id", type=int, location=OpenApiParameter.PATH, description="채택할 답변 ID"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request, question_id: int, answer_id: int) -> Response:
        return Response({"message": "답변 채택 완료"}, status=status.HTTP_200_OK)


class AnswerCommentCreateView(APIView):
    serializer_class = AnswerCommentCreateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=AnswerCommentCreateSerializer,
        description="답변에 대한 댓글 생성",
        tags=["answer"],
    )
    def post(self, request: Request, answer_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
