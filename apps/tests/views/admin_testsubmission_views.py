from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.core.utils.filters import filter_test_submissions
from apps.tests.core.utils.grading import (
    calculate_total_score,
    get_questions_snapshot_from_submission,
    validate_answers_json_format,
)
from apps.tests.core.utils.sorting import sort_by_total_score
from apps.tests.models import TestSubmission
from apps.tests.pagination import AdminTestListPagination
from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_submission_serializers import (
    AdminTestDetailSerializer,
    AdminTestSubmissionListSerializer,
    TestSubmissionFilterSerializer,
)


# 쪽지 시험 응시 내역 전체 목록 조회
@extend_schema(
    tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"],
    parameters=[
        OpenApiParameter(
            name="subject_title",
            type=str,
            location=OpenApiParameter.QUERY,
            description="과목명으로 모든 응시내역 조회",
            required=False,
        ),
        OpenApiParameter(
            name="course_title",
            type=str,
            location=OpenApiParameter.QUERY,
            description="과정명과 기수 고유 ID로 기수가 응시한 모든 응시내역 조회",
            required=False,
        ),
        OpenApiParameter(
            name="generation_number",
            type=int,
            location=OpenApiParameter.QUERY,
            description="과목명, 과정명, 기수 고유 ID로 기수가 응시한 모든 응시내역 조회",
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            enum=["latest", "total_score_desc", "total_score_asc"],
            description="정렬 기준: 최신순(latest), 총점 높은 순(total_score_desc), 총점 낮은 순(total_score_asc)",
        ),
        OpenApiParameter(
            name="page",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본값: 1)",
            required=False,
        ),
    ],
)
class AdminTestSubmissionsView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = AdminTestSubmissionListSerializer

    def get(self, request: Request) -> Response:
        """
        쪽지 시험 응시 내역 목록 조회 API
        """
        filter_serializer = TestSubmissionFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        queryset = TestSubmission.objects.select_related(
            "student__user", "deployment__test", "deployment__generation__course"
        )

        filtered_qs = filter_test_submissions(queryset, filters)

        if any(filters.values()) and not filtered_qs.exists():
            return Response(
                {"detail": "검색어로 조회된 결과가 없습니다."},
                status=404,
            )

        ordering = filters.get("ordering", "latest")
        sorted_submissions = sort_by_total_score(filtered_qs, ordering)

        paginator = AdminTestListPagination()
        page = paginator.paginate_queryset(sorted_submissions, request)  # type: ignore

        serializer = self.serializer_class(page, many=True)
        return Response(
            {"message": "쪽지시험 응시내역 목록 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 상세 조회
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = AdminTestDetailSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        """
        쪽지 시험 응시 내역 상세 조회 API
        """
        try:
            test_submission = TestSubmission.objects.select_related("student", "deployment__test").get(pk=submission_id)
        except TestSubmission.DoesNotExist:
            return Response(
                {"detail": f"{submission_id}에 해당하는 객체가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(instance=test_submission)

        return Response(
            {"message": "쪽지시험 응시내역 목록 상세 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK
        )


# 쪽지 시험 응시 내역 삭제
@extend_schema(tags=["[Admin] Test - submission (쪽지시험 응시 목록/상세/삭제)"])
class AdminTestSubmissionDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def delete(self, request: Request, submission_id: int) -> Response:
        """
        쪽지 시험 응시 내역 삭제 API
        """
        test_submission = get_object_or_404(TestSubmission, pk=submission_id)
        test_submission.delete()
        return Response({"message": f"쪽지시험 응시내역 {submission_id} 삭제 완료"}, status=status.HTTP_200_OK)
