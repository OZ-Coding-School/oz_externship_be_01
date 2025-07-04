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
from apps.users.utils.redis import (
    delete_email_code,
    get_stored_email_code,
    mark_email_as_verified,
    store_email_code,
)


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

        email = serializer.validated_data["email"]
        input_code = serializer.validated_data["verification_code"]

        stored_code = get_stored_email_code(email)

        if stored_code is None:
            return Response({"error": "인증 코드가 만료되었거나 존재하지 않습니다."}, status=status.HTTP_410_GONE)

        if stored_code != input_code:
            return Response({"error": "인증 코드가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        delete_email_code(email)
        mark_email_as_verified(email)

        return Response({"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK)
