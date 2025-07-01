from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.email_auth import (
    EmailSendCodeSerializer,
    EmailVerifyCodeSerializer,
)
from apps.users.utils.email import send_verification_code_to_email
from apps.users.utils.redis import get_stored_email_code, store_email_code


class SendEmailCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailSendCodeSerializer, responses={200: None}, summary="이메일 인증 코드 전송", tags=["auth"]
    )
    def post(self, request: Request) -> Response:
        # 이메일 형식 검증.
        serializer = EmailSendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 이메일 인증코드 생성 -> 이메일 전송.
        email: str = serializer.validated_data["email"]

        code: str = send_verification_code_to_email(email)
        store_email_code(email, code)

        return Response({"message": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)


class VerifyEmailCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailVerifyCodeSerializer,
        responses={200: None, 400: None},
        summary="이메일 인증코드 검증",
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:

        serializer = EmailVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
