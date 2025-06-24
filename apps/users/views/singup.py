from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class SignupAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict[str, Any] = request.data

        required_fields = ["email", "password", "password2", "name", "nickname", "phone_number", "birth_date"]
        for field in required_fields:
            if not data.get(field):
                return Response({
                    "detail": f"{field} 필드는 필수입니다."
                }, status=status.HTTP_400_BAD_REQUEST)

        if data.get("password") != data.get("password2"):
            return Response({
                "detail": "비밀번호가 일치하지 않습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "회원가입이 완료되었습니다."
        }, status=status.HTTP_201_CREATED)