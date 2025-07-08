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
from apps.users.utils.redis_utils import (
    get_phone_code,
    save_phone_code,
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
            return Response(serializer.errors, status=400)

        try:
            phone = serializer.validated_data["phone"]
            phone = normalize_phone_number(phone)  # 국제번호로 변환
            code = generate_code()
            save_phone_code(phone, code)
            send_sms_verification_code(phone, code)
            return Response({"message": "인증번호 전송 성공!"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class VerifyPhoneCodeAPIView(APIView):
    @extend_schema(
        request=VerifyPhoneCodeSerializer,
        responses={200: None},
        tags=["auth"],
        summary="휴대폰 인증번호 검증",
    )
    def post(self, request):
        serializer = VerifyPhoneCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data["phone"]
        input_code = serializer.validated_data["code"]
        real_code = get_phone_code(phone)

        if not real_code:
            return Response({"error": "인증번호가 만료되었거나 존재하지 않습니다."}, status=400)

        if input_code != real_code:
            return Response({"error": "인증번호가 일치하지 않습니다."}, status=400)

        return Response({"message": "인증 성공!"}, status=200)
