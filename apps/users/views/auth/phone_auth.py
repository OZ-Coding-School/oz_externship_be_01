import random
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import PhoneVerificationCode
from apps.users.serializers.auth.phone_auth import (
    PhoneSendCodeSerializer,
    PhoneVerifyCodeSerializer,
)
from apps.users.utils.twilio_utils import send_sms_code


class PhoneSendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
            return Response({"message": "휴대폰 인증코드 전송됨"}, status=200)
        return Response(serializer.errors, status=400)


class PhoneVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PhoneVerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "휴대폰 인증 성공!"})
        return Response(serializer.errors, status=400)
