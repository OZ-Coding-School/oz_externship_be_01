from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.tests.serializers.user_admin_deployment_serializers import CodeValidationRequestSerializer

# MOCK 데이터 (이전과 동일하게 임포트하거나 선언해 주세요)
MOCK_DEPLOYMENTS_DETAILS = {
    101: {
        "test_id": 301, "test_name": "기초 Python 문법 테스트", "subject_name": "core", "question_count": 10,
        "deployment_id": 101, "test_url": "https://ozclass.com/tests/101", "access_code": "aB3dE9",
        "course_name": "오즈 인스턴십", "course_term": "1기", "duration_minutes": 60,
        "started_at": None, "ended_at": None,
        "status": "Activated",
    },
    102: {
        "test_id": 302, "test_name": "자료 구조와 알고리즘 중급 테스트", "subject_name": "liew", "question_count": 15,
        "deployment_id": 102, "test_url": "https://ozclass.com/tests/102", "access_code": "Zk3Lp1",
        "course_name": "백엔드", "course_term": "10기", "duration_minutes": 90,
        "started_at": None, "ended_at": None,
        "status": "Activated",
    },
}

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

        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)
        if details and details.get("access_code") == access_code and details.get("status") == "Activated":
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": details.get("test_name"),
                "deployment_id": deployment_id,
                "duration_time": details.get("duration_minutes", 60)
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "유효하지 않은 참가코드입니다."
        }, status=status.HTTP_400_BAD_REQUEST)
