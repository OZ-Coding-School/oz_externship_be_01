from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class NaverLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict[str, Any] = request.data
        naver_token = data.get("naver_token")

        if naver_token == "mock_naver_token":
            return Response({
                "access_token": "naver_token",
                "refresh_token": "naver_refresh_token",
                "user": {
                    "id": 3,
                    "email": "naver@example.com",
                    "username": "오즈"
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "유효하지 않은 네이버 토큰입니다."
        }, status=status.HTTP_400_BAD_REQUEST)