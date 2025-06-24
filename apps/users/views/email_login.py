# users/views/email_login.py

from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class EmailLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict[str, Any] = request.data
        email: str = data.get("email", "")
        password: str = data.get("password", "")

        if not email or not password:
            return Response(
                {"detail": "empty_fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        if email == "test@example.com" and password == "1234":
            return Response(
                {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "user": {
                        "id": 1,
                        "email": "test@example.com",
                        "username": "오즈",
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "invalid_email_or_password"},
            status=status.HTTP_400_BAD_REQUEST,
        )