from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.kakao_login import KakaoLoginSerializer


class KakaoLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = KakaoLoginSerializer(data=request.data)
        if serializer.is_valid():

            return Response(
                {
                    "access_token": "kakao_access_token",
                    "refresh_token": "kakao_refresh_token",
                    "user": {"id": 2, "email": "kakao@example.com", "username": "카카오유저"},
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
