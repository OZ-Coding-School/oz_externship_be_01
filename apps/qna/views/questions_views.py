from typing import Any

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ...users.models import User
from ..models import Question, QuestionCategory, QuestionImage
from ..permissions import IsStudentPermission
from ..serializers.questions_serializers import (
    MajorQnACategorySerializer,
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

    def get_minor_ids(self, category):
        if category.category_type == "major":
            middle_ids = category.subcategories.values_list("id", flat=True)
            minor_ids = QuestionCategory.objects.filter(parent_id__in=middle_ids).values_list("id", flat=True)
            return list(minor_ids)
        elif category.category_type == "middle":
            minor_ids = category.subcategories.values_list("id", flat=True)
            return list(minor_ids)
        elif category.category_type == "minor":
            return [category.id]
        else:
            return []

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category_id")
        if category_id:
            try:
                category = QuestionCategory.objects.get(id=category_id)
            except QuestionCategory.DoesNotExist:
                return queryset.none()
            minor_ids = self.get_minor_ids(category)
            if minor_ids:
                queryset = queryset.filter(category_id__in=minor_ids)
            else:
                return queryset.none()
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
    permission_classes = [permissions.IsAuthenticated, IsStudentPermission]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionDetailSerializer,
        description="새 질문 생성",
        tags=["questions"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = QuestionCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save(author=request.user)
        return Response({"id": question.id}, status=status.HTTP_201_CREATED)


# 4. 질문 부분 수정 (PATCH)
class QuestionUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudentPermission]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=QuestionUpdateSerializer,
        responses=QuestionDetailSerializer,
        description="질문 부분 수정",
        tags=["questions"],
    )
    def patch(self, request: Request, question_id: int) -> Response:
        question = get_object_or_404(Question, pk=question_id)

        serializer = QuestionUpdateSerializer(question, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = QuestionDetailSerializer(question).data
        return Response(response_data, status=status.HTTP_200_OK)


# 5. 카테고리 목록 조회
class CategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses=MajorQnACategorySerializer(many=True),
        description="Q&A 카테고리 목록 조회",
        tags=["questions"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = (
            QuestionCategory.objects.all()
            .prefetch_related("subcategories", "subcategories__subcategories")
            .filter(Q(parent__isnull=True) & Q(subcategories__isnull=False))
            .distinct()
        )
        serializer = MajorQnACategorySerializer(queryset, many=True)
        resp_data = serializer.data
        return Response(resp_data, status=status.HTTP_200_OK)
