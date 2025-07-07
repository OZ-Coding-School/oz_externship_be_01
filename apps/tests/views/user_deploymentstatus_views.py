from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment
from apps.tests.permissions import IsStudent
from apps.tests.serializers.test_deployment_serializers import (
    TestDeploymentStatusResponseSerializer,
)


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 배포 상태 검증)"],
    summary="쪽지시험 배포 상태 검증 API",
    description=(
        "수강생 권한으로 특정 쪽지시험 배포의 활성화 상태와 오픈 시간을 검증합니다.\n\n"
        "- 배포 상태가 'Deactivated'이거나 오픈 시간이 도래하지 않았다면 응시할 수 없습니다.\n"
        "- 응시 가능 여부를 응답하여 클라이언트가 입장 가능 여부를 안내할 수 있도록 합니다."
    ),
    responses={
        200: TestDeploymentStatusResponseSerializer,
        400: OpenApiResponse(description="시험이 아직 오픈되지 않았거나 비활성화 상태입니다."),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="수강생 권한이 없습니다."),
        404: OpenApiResponse(description="TestDeployment not found."),
    },
)
class UserTestDeploymentStatusView(APIView):
    serializer_class = TestDeploymentStatusResponseSerializer
    permission_classes = [IsStudent]

    def get(self, request, test_deployment_id):
        test_deployment = get_object_or_404(TestDeployment, id=test_deployment_id)

        serializer = self.serializer_class(instance=test_deployment)
        # validate()를 명시적으로 호출해 상태/시간 검증만 수행 (data는 빈 dict로 전달) is_valid() 사용 불가
        serializer.validate({})

        return Response(serializer.data, status=status.HTTP_200_OK)
