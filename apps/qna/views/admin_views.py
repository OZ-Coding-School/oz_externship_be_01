from datetime import datetime

from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import BooleanField, Case, Count, Q, When
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.dummy import dummy
from apps.qna.models import (
    Answer,
    AnswerComment,
    AnswerImage,
    Question,
    QuestionAIAnswer,
    QuestionCategory,
    QuestionImage,
)
from apps.qna.permissions import IsAdminPermission, IsStaffPermission
from apps.qna.serializers.admin_serializers import (
    AdminCategoryCreateSerializer,
    AdminCategoryListSerializer,
    AdminQuestionListPaginationSerializer,
    AdminQuestionListSerializer,
)

dummy.load_dummy_data()


# 카테고리 등록(POST)
class AdminCategoryCreateView(APIView):
    permission_classes = [IsAdminPermission | IsStaffPermission]

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
    permission_classes = [IsAdminPermission | IsStaffPermission]

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="카테고리 삭제",
        description="카테고리 삭제 (Hard Delete) - 하위 카테고리 및 질문 일반질문으로 이동",
        responses={
            200: {"description": "삭제 성공"},
            404: {"description": "카테고리를 찾을 수 없음"},
            400: {"description": "일반질문 카테고리는 삭제할 수 없음"},
        },
    )
    def delete(self, request, category_id: int):
        try:
            # category_id로 카테고리 조회
            category = QuestionCategory.objects.prefetch_related("subcategories", "subcategories__subcategories").get(
                id=category_id
            )

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
                categories_to_delete = self._collect_delete_ids(category)

                # 해당 카테고리 및 하위 카테고리에 속한 질문 일반 카테고리로 이동
                questions_to_move = Question.objects.filter(category__in=categories_to_delete)
                questions_to_move.update(category=general_category)

                # 카테고리 삭제 - QuerySet의 delete() 메서드 사용
                QuestionCategory.objects.filter(id__in=categories_to_delete).delete()

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

    def _collect_delete_ids(self, category):
        collected_ids = [category.id]

        if category.category_type == "major":
            middle_categories = category.subcategories.all()
            collected_ids.extend([c.id for c in middle_categories])

            for middle in middle_categories:
                minor_categories = middle.subcategories.all()
                collected_ids.extend([c.id for c in minor_categories])

        elif category.category_type == "middle":
            minor_categories = category.subcategories.all()
            collected_ids.extend([c.id for c in minor_categories])

        return collected_ids


# 카테고리 목록 조회(GET)
class AdminCategoryListView(APIView):
    permission_classes = [IsAdminPermission | IsStaffPermission]

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


# 질문 목록 조회(GET)
class AdminQuestionListView(APIView):
    permission_classes = [IsAdminPermission | IsStaffPermission]

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="질문 목록 조회",
        responses={200: AdminQuestionListPaginationSerializer},
    )
    def get(self, request: Request) -> Response:
        q = request.query_params
        page = int(q.get("page", 1))
        page_size = min(int(q.get("page_size", 20)), 100)

        queryset = (
            Question.objects.select_related("category", "category__parent", "category__parent__parent", "author")
            .prefetch_related("images", "answers")
            .annotate(
                answer_count=Count("answers", distinct=True),
                has_answer=Case(
                    When(answers__isnull=False, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
        )

        # 검색
        if search := q.get("search", "").strip():
            search_type = q.get("search_type", "title_content")
            if search_type == "author":
                queryset = queryset.filter(author__nickname__icontains=search)
            elif search_type == "title":
                queryset = queryset.filter(title__icontains=search)
            elif search_type == "content":
                queryset = queryset.filter(content__icontains=search)
            else:
                queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))

        # 필터
        if cid := q.get("category_id"):
            try:
                queryset = queryset.filter(category_id=int(cid))
            except ValueError:
                pass
        if ans := q.get("has_answer"):
            queryset = queryset.filter(answer_count__gt=0 if ans == "Y" else 0)

        # 날짜 필터
        for field in ["created", "updated"]:
            for suffix in ["start", "end"]:
                param = f"{field}_{suffix}"
                if val := q.get(param):
                    lookup = f"{field}_at__date__{'gte' if suffix == 'start' else 'lte'}"
                    parsed = self._parse_date(val)
                    if parsed:
                        queryset = queryset.filter(**{lookup: parsed})

        # 정렬
        ordering = q.get("ordering", "-created_at")
        if ordering not in ["created_at", "-created_at", "view_count", "-view_count"]:
            ordering = "-created_at"
        queryset = queryset.order_by(ordering)

        # 페이지네이션
        paginator = Paginator(queryset, page_size)
        try:
            questions = paginator.page(page)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        serializer = AdminQuestionListSerializer(questions, many=True)
        return Response(
            {
                "count": paginator.count,
                "next": self._page_url(request, questions.next_page_number()) if questions.has_next() else None,
                "previous": (
                    self._page_url(request, questions.previous_page_number()) if questions.has_previous() else None
                ),
                "results": serializer.data,
            }
        )

    def _parse_date(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    def _page_url(self, request, page_number):
        query = request.query_params.copy()
        query["page"] = page_number
        return f"{request.build_absolute_uri('?')}?{query.urlencode()}"


# 질문 삭제(DELETE)
class AdminQuestionDeleteView(APIView):
    permission_classes = [IsAdminPermission | IsStaffPermission]

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="질문 삭제",
        description="질문 삭제 (Hard Delete)",
        responses={
            200: {"description": "삭제 성공"},
            404: {"description": "질문을 찾을 수 없음"},
            500: {"description": "서버 오류"},
        },
    )
    def delete(self, request: Request, question_id: int) -> Response:
        try:
            question = Question.objects.select_related("category", "author").get(id=question_id)

            question_info = {
                "id": question.id,
                "title": question.title,
                "content": question.content[:100] + "..." if len(question.content) > 100 else question.content,
                "author_nickname": question.author.nickname if question.author else None,
                "category_name": question.category.name if question.category else None,
                "view_count": question.view_count,
                "created_at": question.created_at,
            }

            answers = Answer.objects.filter(question=question)
            answer_ids = list(answers.values_list("id", flat=True))

            # 사전 삭제 수 카운트 (한 번의 filter 호출로 처리)
            answer_comments_qs = AnswerComment.objects.filter(answer_id__in=answer_ids)
            answer_images_qs = AnswerImage.objects.filter(answer_id__in=answer_ids)
            question_images_qs = QuestionImage.objects.filter(question=question)
            question_ai_answers_qs = QuestionAIAnswer.objects.filter(question=question)

            deleted_counts = {
                "answers_count": answers.count(),
                "answer_comments_count": answer_comments_qs.count(),
                "answer_images_count": answer_images_qs.count(),
                "question_images_count": question_images_qs.count(),
                "question_ai_answers_count": question_ai_answers_qs.count(),
            }

            with transaction.atomic():
                answer_comments_qs.delete()
                answer_images_qs.delete()
                answers.delete()
                question_images_qs.delete()
                question_ai_answers_qs.delete()
                question.delete()

            return Response(
                {
                    "success": True,
                    "message": "질문과 관련된 모든 데이터가 성공적으로 삭제되었습니다.",
                    "deleted_question": question_info,
                    "deleted_related_data": deleted_counts,
                },
                status=status.HTTP_200_OK,
            )

        except Question.DoesNotExist:
            return Response({"error": "해당 질문을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"질문 삭제 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 답변 삭제(DELETE)
class AdminAnswerDeleteView(APIView):
    permission_classes = [IsAdminPermission | IsStaffPermission]

    @extend_schema(
        tags=["QnA (Admin)"],
        summary="답변 삭제",
        description="답변 삭제 (Hard Delete)",
        responses={
            200: {"description": "삭제 성공"},
            404: {"description": "답변을 찾을 수 없음"},
            500: {"description": "서버 오류"},
        },
    )
    def delete(self, request: Request, answer_id: int) -> Response:
        try:
            answer = Answer.objects.select_related("question", "author").get(id=answer_id)

            answer_info = {
                "id": answer.id,
                "question_id": answer.question.id,
                "question_title": answer.question.title,
                "author_nickname": answer.author.nickname if answer.author else None,
                "content": answer.content[:50] + "..." if len(answer.content) > 50 else answer.content,
                "is_adopted": answer.is_adopted,
                "created_at": answer.created_at,
            }

            answer_comments_qs = AnswerComment.objects.filter(answer=answer)
            answer_images_qs = AnswerImage.objects.filter(answer=answer)

            deleted_comments_count = answer_comments_qs.count()
            deleted_images_count = answer_images_qs.count()

            with transaction.atomic():
                answer_comments_qs.delete()
                answer_images_qs.delete()
                answer.delete()

            return Response(
                {
                    "success": True,
                    "message": "답변이 성공적으로 삭제되었습니다.",
                    "deleted_answer": answer_info,
                    "deleted_related_data": {
                        "comments_count": deleted_comments_count,
                        "images_count": deleted_images_count,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Answer.DoesNotExist:
            return Response({"error": "해당 답변을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"답변 삭제 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
