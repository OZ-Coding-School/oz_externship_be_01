from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request

from apps.users.serializers.auth.naver_login import NaverLoginSerializer

class NaverLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = NaverLoginSerializer(data=request.data)
        if serializer.is_valid():

            return Response({
                "access_token": "naver_access_token",
                "refresh_token": "naver_refresh_token",
                "user": {
                    "id": 3,
                    "email": "naver@example.com",
                    "username": "네이버유저"
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)