from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class KakaoLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict[str, Any] = request.data
        kakao_token = data.get("kakao_token")

        if kakao_token == "mock_kakao_token":
            return Response({
                "access_token": "kakao_token",
                "refresh_token": "kakao_refresh_token",
                "user": {
                    "id": 2,
                    "email": "kakao@example.com",
                    "username": "오즈"
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "유효하지 않은 카카오 토큰입니다."
        }, status=status.HTTP_400_BAD_REQUEST)