from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment
from apps.tests.serializers.test_deployment_serializers import (
    UserCodeValidationSerializer,
)


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 참가코드 검증)"],
    request=UserCodeValidationSerializer,
    responses={200: dict, 400: dict, 404: dict},
    summary="쪽지시험 참가코드 검증 API",
    description="path, DB로 test_deployment_id를 받고, DB로 access_code만 받아 참가코드를 검증합니다.",
)
class UserCodeValidationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserCodeValidationSerializer

    def post(self, request: Request, test_deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            test_deployment = TestDeployment.objects.get(id=test_deployment_id)
        except TestDeployment.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 시험 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            data=request.data,
            context={"test_deployment": test_deployment}
        )
        serializer.is_valid(raise_exception=True)

        return Response({"detail": "참가코드가 유효합니다."}, status=status.HTTP_200_OK)
