import random

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.phone_auth import (
    SendPhoneCodeSerializer,
    VerifyPhoneCodeSerializer,
)
from apps.users.utils.twilio_utils import (
    normalize_phone_number,
    send_sms_verification_code,
)


def generate_code() -> str:
    return str(random.randint(100000, 999999))


class SendPhoneCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SendPhoneCodeSerializer,
        responses={200: None},
        tags=["auth"],
        summary="휴대폰 인증 발송",
    )
    def post(self, request):
        serializer = SendPhoneCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            phone = serializer.validated_data["phone"]
            phone = normalize_phone_number(phone)
            send_sms_verification_code(phone)
            return Response({"message": "인증번호 전송 성공!"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPhoneCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyPhoneCodeSerializer,
        responses={200: None},
        tags=["auth"],
        summary="휴대폰 인증번호 검증",
    )
    def post(self, request):
        serializer = VerifyPhoneCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "phone authentication success."}, status=status.HTTP_200_OK)
