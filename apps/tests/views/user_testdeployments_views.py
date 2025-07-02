from typing import Any, Dict, Optional

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.serializers.test_deployment_serializers import (
    UserCodeValidationSerializer,
)

# MOCK 유저 데이터 (예: access_code가 키 역할)
MOCK_USERS: dict[str, dict[str, Any]] = {
    "aB3dE9": {"test_deployment_id": 1, "username": "alice", "email": "alice@example.com"},
    "xY9zQ1": {"test_deployment_id": 2, "username": "bob", "email": "bob@example.com"},
}


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 참가코드 검증)"],
    request=UserCodeValidationSerializer,
    responses={200: dict, 400: dict, 404: dict},
    summary="쪽지시험 참가코드 검증 API",
    description="path로 test_id를 받고, body로 access_code만 받아 참가코드를 검증합니다.",
)
class UserCodeValidationView(APIView):

    permission_classes = [AllowAny]
    serializer_class = UserCodeValidationSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        test_deployment_id: Optional[int] = kwargs.get("test_deployment_id")
        if not test_deployment_id:
            return Response({"detail": "시험 ID(test_deployment_id)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserCodeValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_code: str = serializer.validated_data["access_code"]
        user: Optional[Dict[str, Any]] = MOCK_USERS.get(access_code)

        if not user or user.get("test_deployment_id") != test_deployment_id:
            return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "message": "참가코드가 유효합니다.",
                "test_title": "HTML/CSS 기초 테스트",  # 오타 'HRML' -> 'HTML'
                "deployment_id": test_deployment_id,
                "duration_time": 60,
            },
            status=status.HTTP_200_OK,
        )
