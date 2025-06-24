from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema

from apps.tests.serializers import CodeValidationRequestSerializer

@extend_schema(
    tags=["test"],
    request=CodeValidationRequestSerializer,
    responses={200: dict, 400: dict},
    description="사용자용 참가코드 검증 모의 API"
)
class TestValidateCodeUserView(APIView):
    def post(self, request):
        serializer = CodeValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        deployment_id = serializer.validated_data["deployment_id"]
        access_code = serializer.validated_data["access_code"]

        if deployment_id == 100 and access_code == "USER123":
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": "사용자용 모의시험",
                "deployment_id": deployment_id,
                "duration_time": 45
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "유효하지 않은 참가코드입니다."
        }, status=status.HTTP_400_BAD_REQUEST)
