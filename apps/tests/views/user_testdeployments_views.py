from typing import Any
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.tests.serializers.test_deployment_serializers import UserCodeValidationSerializer

# MOCK 유저 데이터 (예: access_code가 키 역할)
MOCK_USERS: dict[str, dict[str, Any]] = {
    "aB3dE9": {"id": 1, "username": "alice", "email": "alice@example.com"},
    "xY9zQ1": {"id": 2, "username": "bob", "email": "bob@example.com"},
}

@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=UserCodeValidationSerializer,
    responses={200: dict, 400: dict, 404: dict},
)
class UserCodeValidationView(APIView):

    permission_classes = [AllowAny]
    serializer_class = UserCodeValidationSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_code: str = serializer.validated_data["access_code"]

        user = MOCK_USERS.get(access_code)
        if not user:
            return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": "참가코드가 유효합니다.",
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
        }, status=status.HTTP_200_OK)
