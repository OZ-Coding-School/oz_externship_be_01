from typing import Any

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
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


class QuestionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# 1. 질문 목록 조회 (GET)
class QuestionListView(ListAPIView):
    queryset = Question.objects.all().select_related("author", "category")
    serializer_class = QuestionListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = QuestionPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "author__nickname",
        "title",
        "content",
    ]
    ordering = ["-created_at", "-id"]  # 최신순, 2차: 최신순

    def get_queryset(self):
        queryset = super().get_queryset()
        major_id = self.request.query_params.get("major_id")
        middle_id = self.request.query_params.get("middle_id")
        minor_id = self.request.query_params.get("minor_id")
        if major_id:
            queryset = queryset.filter(category__parent__parent__id=major_id)
        if middle_id:
            queryset = queryset.filter(category__parent__id=middle_id)
        if minor_id:
            queryset = queryset.filter(category_id=minor_id)
        answered = self.request.query_params.get("answered")
        if answered == "true":
            queryset = queryset.filter(answer_set__isnull=False)
        elif answered == "false":
            queryset = queryset.filter(answer_set__isnull=True)
        return queryset

    def list(self, request, *args, **kwargs):
        # 1. 캐시 키를 URL+쿼리 파라미터 조합으로 생성
        cache_key = f"question_list:{request.get_full_path()}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # 2. 캐시에 없으면 원래 로직대로 조회
        response = super().list(request, *args, **kwargs)
        # 3. 캐시 저장 (예: 2분간)
        cache.set(cache_key, response.data, timeout=120)
        return response


# 2. 질문 상세 조회 (GET)
class QuestionDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=QuestionDetailSerializer,
        description="질문 상세 조회",
        tags=["questions"],
    )
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        question = get_object_or_404(Question, pk=question_id)
        serializer = QuestionDetailSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 3. 새 질문 생성 (POST)
class QuestionCreateView(APIView):
    permission_classes = [permissions.AllowAny]  # TODO: IsAuthenticated, IsStudentUser
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionDetailSerializer,
        description="새 질문 생성",
        tags=["questions"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 이미지가 빈 값이면 제거
        data = request.data.copy()
        if "image_files" in data:
            images = data.getlist("image_files") if hasattr(data, "getlist") else data["image_files"]
            if isinstance(images, list):
                if hasattr(data, "setlist"):
                    data.setlist("image_files", [img for img in images if img])
                else:
                    data["image_files"] = [img for img in images if img]
        serializer = QuestionCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save(author=request.user)
        return Response({"id": question.id}, status=status.HTTP_201_CREATED)


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
