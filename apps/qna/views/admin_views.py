from typing import Any

from django.db import transaction
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.dummy import dummy
from apps.qna.models import QuestionCategory
from apps.qna.serializers.admin_serializers import (
    AdminCategoryCreateSerializer,
    AdminCategoryListSerializer,
    AdminQuestionImageSerializer,
    AdminQuestionListSerializer,
    MajorQnACategorySerializer,
)

dummy.load_dummy_data()


# 카테고리 등록(POST)
class AdminCategoryCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["QnA (Admin)"],
        description="새로운 카테고리 등록",
        summary="카테고리 등록",
        request=AdminCategoryCreateSerializer,
        responses=AdminCategoryListSerializer,
    )
    def post(self, request: Request) -> Response:
        serializer = AdminCategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            response_serializer = AdminCategoryCreateSerializer(category)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 카테고리 삭제(DELETE)
class AdminCategoryDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["QnA (Admin)"],
        description="카테고리를 삭제합니다. 하위 카테고리나 질문이 있는 경우 삭제가 제한됩니다.(미완성)",
        summary="미완성",
        request=AdminCategoryListSerializer,
        responses=AdminCategoryListSerializer,
    )
    def delete(self, request: Request, category_id: int) -> Response:
        try:
            category = QuestionCategory.objects.prefetch_related("subcategories", "questions").get(id=category_id)

            # 하위 카테고리 존재 확인
            if category.subcategories.exists():
                return Response(
                    {"detail": "하위 카테고리가 존재하여 삭제할 수 없습니다. 먼저 하위 카테고리를 삭제해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 해당 카테고리에 속한 질문 존재 확인
            if category.questions.exists():
                return Response(
                    {
                        "detail": "해당 카테고리에 질문이 존재하여 삭제할 수 없습니다. 먼저 질문을 다른 카테고리로 이동하거나 삭제해주세요."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 삭제 실행
            with transaction.atomic():
                category.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except QuestionCategory.DoesNotExist:
            return Response({"detail": "해당 카테고리가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)


# 카테고리 목록 조회(GET)
class AdminCategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="카테고리 목록 조회",
        description="카테고리 목록 조회 (검색 및 필터링 지원)",
        parameters=[
            OpenApiParameter(name="search", description="카테고리 이름 검색", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(
                name="category_type",
                description="카테고리 타입 필터 (major, middle, minor)",
                required=False,
                type=OpenApiTypes.STR,
                enum=["major", "middle", "minor"],
            ),
            OpenApiParameter(
                name="parent_id", description="부모 카테고리 ID로 필터링", required=False, type=OpenApiTypes.INT
            ),
        ],
        responses={200: MajorQnACategorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 쿼리 파라미터 추출
        search = request.query_params.get("search", "").strip()
        category_type = request.query_params.get("category_type", "").strip()
        parent_id = request.query_params.get("parent_id", "").strip()

        # 기본 쿼리셋
        base_queryset = QuestionCategory.objects.all()

        # 검색 조건 적용
        if search:
            base_queryset = base_queryset.filter(
                Q(name__icontains=search)
                | Q(subcategories__name__icontains=search)
                | Q(subcategories__subcategories__name__icontains=search)
            ).distinct()

        # 카테고리 타입 필터
        if category_type:
            if category_type == "major":
                base_queryset = base_queryset.filter(parent__isnull=True)
            elif category_type == "middle":
                base_queryset = base_queryset.filter(parent__isnull=False, parent__parent__isnull=True)
            elif category_type == "minor":
                base_queryset = base_queryset.filter(parent__parent__isnull=False)

        # 부모 카테고리 ID 필터
        if parent_id:
            try:
                parent_id = int(parent_id)
                base_queryset = base_queryset.filter(parent_id=parent_id)
            except ValueError:
                return Response({"error": "parent_id must be a valid integer"}, status=status.HTTP_400_BAD_REQUEST)

        # 계층 구조로 반환
        if not category_type or category_type == "major":
            # 대분류만 필터하고 하위 카테고리까지 포함
            hierarchical_queryset = (
                base_queryset.filter(parent__isnull=True)
                .prefetch_related("subcategories", "subcategories__subcategories")
                .distinct()
            )
            serializer = MajorQnACategorySerializer(hierarchical_queryset, many=True)
        else:
            # 중분류나 소분류의 경우 평면 구조로 반환
            serializer = AdminCategoryListSerializer(base_queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# 질의응답 상세 조회
class AdminQnaDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["QnA (Admin)"], description="조회할 질의응답 ID", summary="미완성")
    def get(self, request: Request, question_id: int, *args: Any, **kwargs: Any) -> Response:
        # 1. 질문 찾기
        question = next((q for q in dummy.DUMMY_QUESTIONS if q.id == question_id), None)
        if not question:
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 카테고리
        category = question.category
        category_data = {
            "id": category.id,
            "name": category.name,
            "parent": category.parent.id if category.parent else None,
            "type": "parent" if category.parent is None else "child",
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }

        # 3. 질문 이미지들
        images = [
            {
                "id": img.id,
                "img_url": img.img_url,
                "created_at": img.created_at,
                "updated_at": img.updated_at,
            }
            for img in dummy.DUMMY_QUESTION_IMAGES
            if getattr(img.question, "id", None) == question_id
        ]

        # 4. 답변들 (답변 이미지 + 댓글 포함)
        answers = []
        for answer in dummy.DUMMY_ANSWERS:
            if getattr(answer.question, "id", None) != question_id:
                continue

            # 답변 이미지 (id 포함)
            answer_images = [
                {
                    "id": img.id,
                    "img_url": img.img_url,
                    "created_at": img.created_at,
                    "updated_at": img.updated_at,
                }
                for img in dummy.DUMMY_ANSWER_IMAGES
                if img.answer.id == answer.id
            ]

            # 답변 댓글
            answer_comments = [
                {
                    "content": comment.content,
                    "author": comment.author.id if comment.author else None,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                }
                for comment in dummy.DUMMY_ANSWER_COMMENTS
                if comment.answer.id == answer.id
            ]

            answers.append(
                {
                    "id": answer.id,
                    "content": answer.content,
                    "author": answer.author.id if answer.author else None,
                    "is_adopted": answer.is_adopted,
                    "created_at": answer.created_at,
                    "images": answer_images,
                    "comments": answer_comments,
                }
            )

        # 5. 최종 응답
        data = {
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "author": question.author.id if question.author else None,
            "view_count": question.view_count,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
            "category": category_data,
            "images": images,
            "answers": answers,
        }

        return Response(data, status=status.HTTP_200_OK)


# 질문 목록 조회
class AdminQuestionListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["QnA (Admin)"], description="조회할 질문 ID", summary="미완성")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminQuestionListSerializer(dummy.DUMMY_QUESTIONS, many=True)
        resp_data = serializer.data
        for data in resp_data:
            images = [image for image in dummy.DUMMY_QUESTION_IMAGES if data["id"] == image.question.id]
            data["images"] = AdminQuestionImageSerializer(images, many=True).data
        return Response(resp_data, status=status.HTTP_200_OK)


# 질문 삭제
class AdminQuestionDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["QnA (Admin)"], description="삭제할 질문 ID", summary="미완성")
    def delete(self, request: Request, question_id: int) -> Response:
        if not any(q.id == question_id for q in dummy.DUMMY_QUESTIONS):
            return Response({"detail": "해당 질문이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 원래는 이런 방식이 아닌데 더미라서 orm을 사용할 수 없기에 이렇게 합니다.
        dummy.DUMMY_QUESTIONS = [q for q in dummy.DUMMY_QUESTIONS if q.id != question_id]
        return Response(status=status.HTTP_204_NO_CONTENT)


# 답변 삭제
class AdminAnswerDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["QnA (Admin)"], description="삭제할 답변 ID", summary="미완성")
    def delete(self, request: Request, answer_id: int) -> Response:
        if not any(q.id == answer_id for q in dummy.DUMMY_ANSWERS):
            return Response({"detail" "해당 답변이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 원래는 이런 방식이 아닌데 더미라서 orm을 사용할 수 없기에 이렇게 합니다.
        dummy.DUMMY_ANSWERS = [q for q in dummy.DUMMY_ANSWERS if q.id != answer_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
