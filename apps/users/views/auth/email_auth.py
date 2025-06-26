from drf_spectacular.utils import extend_schema
from rest_framework import status
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

    @extend_schema(request=EmailSendCodeSerializer, responses={200: None}, tags=["auth"])
    def post(self, request: Request) -> Response:
        serializer = EmailSendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email: str = serializer.validated_data["email"]
        code: str = send_verification_code_to_email(email)
        store_email_code(email, code)

        return Response({"message": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)


class VerifyEmailCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=EmailVerifyCodeSerializer, responses={200: None, 400: None}, tags=["auth"])
    def post(self, request: Request) -> Response:
        serializer = EmailVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email: str = serializer.validated_data["email"]
        code: str = serializer.validated_data["code"]
        stored_code = get_stored_email_code(email)

        if stored_code is None:
            return Response(
                {"message": "인증 코드가 만료되었거나 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        if code != stored_code:
            return Response({"message": "인증 코드가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
