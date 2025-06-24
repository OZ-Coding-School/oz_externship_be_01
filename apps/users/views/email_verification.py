from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class EmailVerificationAPIView(APIView):
    def post(self, request: Request) -> Response:
        data: Dict[str, Any] = request.data
        email = data.get("email")

        if not email:
            return Response({
                "detail": "이메일은 필수입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        if email == "duplicate@example.com":
            return Response({
                "detail": "이미 인증 요청된 이메일입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "인증 코드가 이메일로 전송되었습니다."
        }, status=status.HTTP_200_OK)