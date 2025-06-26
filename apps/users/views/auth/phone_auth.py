from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.phone_auth import (
    PhoneSendCodeSerializer,
    PhoneVerifyCodeSerializer,
)


def send_sms_code(phone_number: str, code: str) -> None:
    pass  # Twilio 통신 로직


class PhoneSendCodeView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PhoneSendCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone_number"]
            code = "123456"
            send_sms_code(phone, code)
            return Response({"message": "휴대폰 인증코드 전송됨"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneVerifyCodeView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PhoneVerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "휴대폰 인증 성공"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
