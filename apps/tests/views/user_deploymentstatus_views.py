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

    def get(self, request: Request, test_deployment_id) -> Response:

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
        response_data = {
            "deployment_id": test_deployment_id,
            "message": "응시가 가능합니다.",
            "status": status_value,
            "requested_at": now.isoformat(),
            "open_at": open_at.isoformat(),
            "close_at": close_at.isoformat(),
        }
        # 성공 응답
        serializer = self.serializer_class(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
