import random

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.find_email_phone_verification import (
    SendPhoneCodeForEmailSerializer,
    VerifyPhoneCodeForEmailFindSerializer,
)
from apps.users.serializers.auth.phone_auth import (
    SendPhoneCodeSerializer,
)
from apps.users.utils.twilio_utils import (
    normalize_phone_number,
    send_sms_verification_code,
)


def generate_code() -> str:
    return str(random.randint(100000, 999999))


class EmailFindPhoneSendCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SendPhoneCodeSerializer,
        responses={200: None},
        tags=["account-find"],
        description="이메일 찾기 전용 인증번호를 휴대폰으로 전송합니다.",
    )
    def post(self, request):
        serializer = SendPhoneCodeForEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            phone = serializer.validated_data["phone"]
            phone = normalize_phone_number(phone)
            send_sms_verification_code(phone)
            return Response({"message": "인증번호 전송 성공!"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailFindPhoneVerifyCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyPhoneCodeForEmailFindSerializer,
        responses={200: None},
        tags=["account-find"],
        summary="[이메일 찾기] 휴대폰 인증번호 확인",
    )
    def post(self, request):
        serializer = VerifyPhoneCodeForEmailFindSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "phone authentication success."}, status=status.HTTP_200_OK)
