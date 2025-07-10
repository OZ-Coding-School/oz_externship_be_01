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
from apps.qna.models import Question, QuestionCategory
from apps.qna.serializers.admin_serializers import (
    AdminCategoryCreateSerializer,
    AdminCategoryListSerializer,
    AdminQuestionImageSerializer,
    AdminQuestionListSerializer,
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
    permission_classes = [AllowAny]  # ⚠️ 추후 관리자 권한으로 변경 필요

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="카테고리 삭제",
        description="카테고리 삭제 (Hard Delete) - 하위 카테고리 및 질문 일반질문으로 이동",
        parameters=[
            OpenApiParameter(
                name="category_id",
                description="삭제할 카테고리 ID",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        responses={
            200: {"description": "삭제 성공"},
            404: {"description": "카테고리를 찾을 수 없음"},
            400: {"description": "일반질문 카테고리는 삭제할 수 없음"},
        },
    )
    def delete(self, request, category_id):
        try:
            # category_id로 카테고리 조회
            category = QuestionCategory.objects.get(id=category_id)

            if category.category_type == "general":
                return Response({"error": "일반질문 카테고리는 삭제할 수 없습니다."}, status=400)

            # 일반질문 카테고리 확보 (없으면 생성)
            general_category, created = QuestionCategory.objects.get_or_create(
                category_type="general",
                defaults={
                    "name": "일반질문",
                    "parent": None,
                },
            )

            with transaction.atomic():
                # 삭제할 카테고리들 수집 (하위 카테고리 포함)
                categories_to_delete = self._collect_subcategories(category)

                # 해당 카테고리 및 하위 카테고리에 속한 질문 일반 카테고리로 이동
                questions_to_move = Question.objects.filter(category__in=categories_to_delete)
                questions_to_move.update(category=general_category)

                # 카테고리 삭제
                for cat in categories_to_delete:
                    cat.delete()

                return Response(
                    {
                        "success": True,
                        "message": "카테고리가 성공적으로 삭제되었습니다.",
                        "deleted_category": {
                            "id": category.id,
                            "name": category.name,
                            "category_type": category.category_type,
                        },
                        "moved_to_category": {
                            "id": general_category.id,
                            "name": general_category.name,
                        },
                    },
                    status=200,
                )

        except QuestionCategory.DoesNotExist:
            return Response({"error": "해당 카테고리를 찾을 수 없습니다."}, status=404)
        except Exception as e:
            return Response({"error": f"카테고리 삭제 중 오류가 발생했습니다: {str(e)}"}, status=500)

    def _collect_subcategories(self, category):
        # 해당 카테고리 및 하위 카테고리들을 순차적으로 수집
        categories = [category]

        if category.category_type == "major":
            # 대분류인 경우: 중분류와 그 하위 소분류들까지 모두 수집
            middle_categories = category.subcategories.filter(category_type="middle")
            categories.extend(middle_categories)
            for middle in middle_categories:
                minor_categories = middle.subcategories.filter(category_type="minor")
                categories.extend(minor_categories)

        elif category.category_type == "middle":
            # 중분류인 경우: 하위 소분류들까지 수집
            minor_categories = category.subcategories.filter(category_type="minor")
            categories.extend(minor_categories)

        # minor나 general인 경우 해당 카테고리만 삭제 (이미 categories에 포함됨)

        return categories


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
        ],
        responses={200: AdminCategoryListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 쿼리 파라미터 추출
        search = request.query_params.get("search", "").strip()
        category_type = request.query_params.get("category_type", "").strip()

        # 기본 쿼리셋
        queryset = QuestionCategory.objects.all().prefetch_related("subcategories", "subcategories__subcategories")

        if search:
            queryset = queryset.filter(name__icontains=search)

        # 카테고리 타입 필터
        if category_type:
            if category_type == "major":
                queryset = queryset.filter(Q(parent__isnull=True) & Q(subcategories__isnull=False)).distinct()
            elif category_type == "middle":
                queryset = queryset.filter(Q(parent__isnull=False) & Q(subcategories__isnull=False)).distinct()

            elif category_type == "minor":
                queryset = queryset.filter(Q(parent__isnull=False) & Q(subcategories__isnull=True)).distinct()
            else:
                return Response({"detail": "category_type query parameter invalid."})

        serializer = AdminCategoryListSerializer(queryset, many=True)

        # 검색 결과가 없는 경우 에러 반환
        if not serializer.data:
            return Response({"error": "해당 카테고리가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

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
