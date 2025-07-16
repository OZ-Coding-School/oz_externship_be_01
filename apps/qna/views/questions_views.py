from typing import Any

from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Question, QuestionCategory
from ..permissions import IsStudentPermission
from ..serializers.questions_serializers import (
    MajorQnACategorySerializer,
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateSerializer,
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
    ordering = ["-created_at", "-id"]

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
        query_params = request.query_params
        param_keys = set(query_params.keys())

        # 1페이지만 캐싱 (파라미터가 없거나 page=1만 있을 때만 캐싱)
        is_main = param_keys == set() or (param_keys == {"page"} and query_params.get("page") == "1")

        if is_main:
            cache_key = f"question_list:/api/v1/qna/questions/"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response)

            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=3600)
            return response
        else:
            # 나머지(검색, 필터, 2페이지~ 등)는 항상 DB에서
            return super().list(request, *args, **kwargs)


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

        # "최신순 1페이지, 필터·검색 없는 상태" 키에만 반영
        # 실제로 첫 페이지 요청시 쿼리파라미터 없는 경우 아래와 같이 캐시가 저장됨
        page1_key = "question_list:/api/v1/qna/questions/"
        cached = cache.get(page1_key)
        if cached:
            from ..serializers.questions_serializers import QuestionListSerializer

            new_item = QuestionListSerializer(question).data
            # 맨 앞에 추가
            cached["results"].insert(0, new_item)
            cached["count"] += 1
            # 10개 유지
            if len(cached["results"]) > 10:
                cached["results"] = cached["results"][:10]
            cache.set(page1_key, cached, timeout=3600)

        response_data = QuestionDetailSerializer(question).data
        return Response(response_data, status=status.HTTP_201_CREATED)


# 4. 질문 부분 수정 (PATCH)
class QuestionUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudentPermission]

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
        return Response(serializer.data, status=status.HTTP_200_OK)
