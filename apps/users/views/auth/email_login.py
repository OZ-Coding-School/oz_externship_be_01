from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request

from apps.users.serializers.auth.email_login import EmailLoginSerializer

class EmailLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            if email == "test@example.com" and password == "1234":
                return Response({
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "user": {
                        "id": 1,
                        "email": email,
                        "username": "오즈"
                    }
                }, status=status.HTTP_200_OK)
            return Response({"detail": "invalid_email_or_password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)