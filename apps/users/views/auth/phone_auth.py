from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import timedelta
from django.utils import timezone
import random
from drf_spectacular.utils import extend_schema

from apps.users.models import PhoneVerificationCode
from apps.users.serializers.auth.phone_auth import (
    PhoneSendCodeSerializer,
    PhoneVerifyCodeSerializer,
)
from apps.users.utils.twilio_utils import send_sms_code


class PhoneSendCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PhoneSendCodeSerializer,
        responses={200: None, 400: None},
        tags=["auth"],
        summary="휴대폰 인증코드 전송"
    )
    def post(self, request: Request) -> Response:
        serializer = PhoneSendCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone_number"]
            code = str(random.randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=5)

            PhoneVerificationCode.objects.create(
                phone_number=phone,
                code=code,
                expires_at=expires_at,
            )

            send_sms_code(phone, code)
            return Response({"message": "휴대폰 인증코드 전송됨"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PhoneVerifyCodeSerializer,
        responses={200: None, 400: None},
        tags=["auth"],
        summary="휴대폰 인증코드 검증"
    )
    def post(self, request: Request) -> Response:
        serializer = PhoneVerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        verification = (
            PhoneVerificationCode.objects
            .filter(phone_number=phone, code=code)
            .order_by("-created_at")
            .first()
        )

        if not verification:
            return Response({"detail": "인증 코드가 일치하지 않습니다."}, status=400)

        if verification.expires_at < timezone.now():
            return Response({"detail": "인증 코드가 만료되었습니다."}, status=400)

        return Response({"message": "휴대폰 인증 성공"})