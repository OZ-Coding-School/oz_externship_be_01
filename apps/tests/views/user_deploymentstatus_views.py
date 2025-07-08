from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment
from apps.tests.permissions import IsStudent


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 배포 상태 검증)"],
    summary="쪽지시험 배포 상태 검증 API",
    description=(
        "수강생 권한으로 특정 쪽지시험 배포의 활성화 상태와 오픈 시간을 검증합니다.\n\n"
        "- 배포 상태가 'Deactivated'이거나 오픈 시간이 도래하지 않았다면 응시할 수 없습니다.\n"
        "- 모든 검증을 통과한 경우 응시 가능 메시지를 반환합니다."
    ),
    responses={
        200: OpenApiResponse(description="응시 가능"),
        400: OpenApiResponse(description="시험이 아직 오픈되지 않았거나 비활성화 상태입니다."),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="수강생 권한이 없습니다."),
        404: OpenApiResponse(description="TestDeployment not found."),
    },
)
class UserTestDeploymentStatusView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, test_deployment_id):
        deployment = get_object_or_404(TestDeployment, id=test_deployment_id)
        now = timezone.now()

        if deployment.status != TestDeployment.TestStatus.ACTIVATED:
            return Response({"detail": "시험이 비활성화 상태입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if now < deployment.open_at:
            return Response(
                {"detail": "시험 오픈 시간이 아직 도래하지 않았습니다. 참가할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if now > deployment.close_at:
            return Response(
                {"detail": "시험 응시 시간이 마감되었습니다. 참가할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "응시가 가능합니다."}, status=status.HTTP_200_OK)
