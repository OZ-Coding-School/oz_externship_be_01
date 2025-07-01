# apps/tests/views/mock_dashboard_views.py

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(
    tags=["[Admin] Test - Dashboard (쪽지시험 대시보드 Mock API)"],
    parameters=[
        OpenApiParameter(name="test_id", required=True, type=int, description="조회할 쪽지시험 ID"),
        OpenApiParameter(
            name="type",
            required=True,
            type=str,
            description="통계 유형: average_by_generation | score_vs_time | score_by_subject",
        ),
        OpenApiParameter(name="generation_id", required=False, type=int, description="기수 ID (score_by_subject 전용)"),
    ],
)
class TestDashboardView(APIView):
    permission_classes = [AllowAny]  # 관리자/스태프만 접근 가능

    def get(self, request: Request) -> Response:
        chart_type = request.query_params.get("type")
        test_id = request.query_params.get("test_id")
        generation_id = request.query_params.get("generation_id")

        if not test_id or not chart_type:
            raise ValidationError("test_id와 type은 필수입니다.")

        if chart_type == "average_by_generation":
            return Response(
                {
                    "type": "average_by_generation",
                    "test_title": "HTML/CSS 기초",
                    "data": [
                        {"generation": "1기", "average_score": 75},
                        {"generation": "2기", "average_score": 80},
                        {"generation": "3기", "average_score": 70},
                    ],
                }
            )

        elif chart_type == "score_vs_time":
            return Response(
                {
                    "type": "score_vs_time",
                    "test_title": "JS 기초",
                    "data": [
                        {"student_id": 101, "score": 85, "elapsed_minutes": 32},
                        {"student_id": 102, "score": 60, "elapsed_minutes": 45},
                    ],
                }
            )

        elif chart_type == "score_by_subject":
            if not generation_id:
                raise ValidationError("score_by_subject 타입에는 generation_id가 필요합니다.")
            return Response(
                {
                    "type": "score_by_subject",
                    "generation": "4기",
                    "data": [
                        {"subject": "HTML", "average_score": 82},
                        {"subject": "CSS", "average_score": 77},
                        {"subject": "JS", "average_score": 71},
                    ],
                }
            )

        else:
            return Response({"detail": "지원하지 않는 type입니다."}, status=status.HTTP_400_BAD_REQUEST)
