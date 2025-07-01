from datetime import datetime, timedelta

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.serializers.test_deployment_serializers import (
    TestDeploymentStatusValidateSerializer,
)


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 배포 상태 검증)"],
)
class TestDeploymentStatusView(APIView):
    serializer_class = TestDeploymentStatusValidateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        deployment_id = serializer.validated_data["deployment_id"]

        # Mock: deployment_id == 9999는 없는 배포로 예외 처리
        if deployment_id == 9999:
            return Response(
                {"detail": "해당 배포를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mock 배포 정보 생성
        now = datetime.now()
        open_at = now - timedelta(minutes=10)  # 이미 오픈됨
        close_at = now + timedelta(minutes=50)  # 아직 마감 전
        status_value = "Activated"  # 활성화 상태

        # 상태와 open 시간 검증
        if status_value != "Activated" or now < open_at:
            return Response(
                {"detail": "해당 시험은 아직 오픈되지 않았거나 비활성화 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 성공 응답
        return Response(
            {
                "message": "응시가 가능합니다.",
                "status": status_value,
                "now": now.isoformat(),
                "open_at": open_at.isoformat(),
                "close_at": close_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )
