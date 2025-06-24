from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.tests.serializers import CodeValidationRequestSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


@extend_schema(
    methods=["POST"],
    description=" 관리자용 참가코드 검증 모의 API",
    request=CodeValidationRequestSerializer,
    responses={200: dict, 400: dict},
    tags=["test"]
)
class TestValidateCodeAdminView(APIView):
    def post(self, request):
        serializer = CodeValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        deployment_id = serializer.validated_data["deployment_id"]
        access_code = serializer.validated_data["access_code"]

        if deployment_id == 999 and access_code == "ADMIN123":
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": "관리자용 모의시험",
                "deployment_id": deployment_id,
                "duration_time": 60
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "유효하지 않은 참가코드입니다."
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["PATCH"],
    parameters=[
        OpenApiParameter(name="deployment_id", required=True, type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        200: dict,
        403: {"description": "권한 없음 또는 테스트 대상 아님"},
    },
    description="쪽지시험 배포 상태를 활성화/비활성화로 토글하는 MOCK API"
)
class TestDeploymentStatusView(APIView):
    def patch(self, request, deployment_id):
        if deployment_id == 999:
            return Response(
                {
                    "deployment_id": deployment_id,
                    "status": "Activated",
                    "message": "모의 API - 배포 상태가 성공적으로 변경되었습니다."
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "모의 API는 지정된 배포 ID(999)에서만 작동합니다."},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    methods=["DELETE"],
    parameters=[
        OpenApiParameter(name="deployment_id", required=True, type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        204: None,
        403: {"description": "권한 없음 또는 테스트 대상 아님"},
    },
    description="쪽지시험 배포 삭제 MOCK API"
)
class DeleteMiniTestDeploymentView(APIView):
    def delete(self, request, deployment_id):
        if deployment_id == 999:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"detail": "존재하지 않는 배포입니다."},
            status=status.HTTP_403_FORBIDDEN
        )
