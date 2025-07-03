from typing import Any, Optional
from urllib import request

from django.views.generic import detail
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

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        test_deployment_id: Optional[int] = kwargs.get("test_deployment_id")
        if not test_deployment_id:
            return Response({"detail": "시험 ID(test_deployment_id)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_code = serializer.validated_data["access_code"]

        try:
            deployment = TestDeployment.objects.get(id=test_deployment_id, access_code=access_code, status="Activated")
        except TestDeployment.DoesNotExist:
            return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "detail": "참가코드가 유효합니다.",
                "test_title": deployment.test.title,
                "deployment_id": deployment.id,
                "duration_time": deployment.duration_time,
            },
            status=status.HTTP_200_OK,
        )
