from datetime import datetime
from typing import Any

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ...users.models import User
from ..models import Question, QuestionCategory, QuestionImage
from ..serializers.questions_serializers import (
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionImageSerializer,
    QuestionListSerializer,
    QuestionUpdateSerializer,
)

# 1. 더미 사용자
DUMMY_USER = User(id=1, email="mock@example.com", nickname="oz_student", profile_image_url="/media/mock_user.png")

# 2. 더미 질문 + 이미지 포함
DUMMY_QUESTIONS = []
DUMMY_QUESTION_IMAGES = []
for i in range(1, 4):
    question = Question(
        id=i,
        title=f"샘플 질문 제목 {i}",
        content=f"샘플 질문 내용 {i}",
        author=DUMMY_USER,
        category=QuestionCategory(id=3, name="오류"),
        created_at=timezone.now(),
    )
    DUMMY_QUESTIONS.append(question)

for q in DUMMY_QUESTIONS:
    # 더미 이미지 (2장씩)
    DUMMY_QUESTION_IMAGES.append(
        QuestionImage(id=1, question=q, img_url=f"/media/sample{i}_1.png", created_at=timezone.now())
    )
    DUMMY_QUESTION_IMAGES.append(
        QuestionImage(id=2, question=q, img_url=f"/media/sample{i}_2.png", created_at=timezone.now())
    )


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
        resp_data = serializer.data
        for data in resp_data:
            images = [image for image in DUMMY_QUESTION_IMAGES if data["id"] == image.question.id]
            data["images"] = QuestionImageSerializer(images, many=True).data
        return Response(resp_data, status=status.HTTP_200_OK)


# 2. 질문 상세 조회 (GET)
class QuestionDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=QuestionDetailSerializer,
        description="질문 상세 조회",
        tags=["questions"],
    )
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 1. 질문 찾기
        item = next((q for q in DUMMY_QUESTIONS if q.id == question_id), None)
        if not item:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 직렬화
        serializer = QuestionDetailSerializer(item)
        data = serializer.data

        # 3. 관련 이미지 mock 추가
        images = [img for img in DUMMY_QUESTION_IMAGES if getattr(img.question, "id", img.question) == question_id]
        data["images"] = QuestionImageSerializer(images, many=True).data

        return Response(data, status=status.HTTP_200_OK)


# 3. 새 질문 생성 (POST)
class QuestionCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionDetailSerializer,
        description="새 질문 생성",
        tags=["questions"],
    )
    def post(self, request: Request) -> Response:
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = Question(
            id=1,
            category=QuestionCategory(
                id=serializer.validated_data["category_id"],
                name="예시 카테고리",
            ),
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            author=User(id=1, email="mock@example.com", nickname="oz_student", profile_image_url="/media/mock.png"),
            view_count=10,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        question_images = [
            QuestionImage(
                id=i,
                img_url=f"/media/{image.name}",
            )
            for i, image in enumerate(serializer.validated_data["image_files"])
        ]
        response_data = QuestionCreateSerializer(question).data
        response_data["images"] = [image.img_url for image in question_images]
        return Response(response_data, status=status.HTTP_201_CREATED)


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
        # 1. 해당 mock 질문 찾기
        question = next((q for q in DUMMY_QUESTIONS if q.id == question_id), None)
        if not question:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 데이터 검증
        serializer = QuestionUpdateSerializer(data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # 3. mock 질문 내용 수정
        if "title" in validated:
            question.title = validated["title"]
        if "content" in validated:
            question.content = validated["content"]
        if "category_id" in validated:
            question.category = QuestionCategory(id=validated["category_id"], name="카테고리 예시")

        # 4. mock 이미지 수정 (단순 교체)
        if "image_files" in validated:
            for i, img in enumerate(DUMMY_QUESTION_IMAGES):
                if img.question.id == question_id and i < len(validated["image_files"]):
                    img.img_url = f"/media/{validated['image_files'][i].name}"

        # 5. 응답
        response_data = QuestionDetailSerializer(question).data
        images = [img for img in DUMMY_QUESTION_IMAGES if img.question.id == question_id]
        response_data["images"] = QuestionImageSerializer(images, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)
