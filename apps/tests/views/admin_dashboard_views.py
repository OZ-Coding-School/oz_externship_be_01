from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_dashboard_serializers import DashboardSerializer


@extend_schema(
    tags=["[Admin] Test - Dashboard (쪽지시험 대시보드 API)"],
    parameters=[
        OpenApiParameter(
            name="type",
            required=True,
            type=str,
            description="통계 유형 (average_by_generation | score_vs_time | score_by_subject)",
        ),
        OpenApiParameter(
            name="test_id", required=False, type=int, description="쪽지시험 ID (average_by_generation, score_vs_time용)"
        ),
        OpenApiParameter(name="generation_id", required=False, type=int, description="기수 ID (score_by_subject용)"),
    ],
    responses={
        200: DashboardSerializer,
        400: OpenApiResponse(description="잘못된 요청 (파라미터 누락/유효하지 않은 값)"),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않음"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="쪽지시험 또는 기수를 찾을 수 없음"),
    },
)
# 관리자용 쪽지시험 통계 대시보드 API
class TestDashboardView(APIView):
    # 관리자 또는 스태프만 접근 가능
    permission_classes = [IsAdminOrStaff]
    serializer_class = DashboardSerializer

    # GET 요청 처리 (쿼리 파라미터 기반 통계 제공)
    def get(self, request):
        # 요청 파라미터 검증 및 객체 주입
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 통계 응답 데이터 생성
        data = serializer.get_response_data()

        # JSON 응답 반환
        return Response(data)
