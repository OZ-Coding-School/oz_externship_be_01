# apps/tests/views/test_user_view.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
def mock_validate_code_user(request):
    """
     사용자용 참가코드 검증 모의 API
    """
    deployment_id = request.data.get("deployment_id")
    access_code = request.data.get("access_code")

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
