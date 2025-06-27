from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.find_account_serializers import (
    EmailFindRequestSerializer,
    EmailFindResponseSerializer,
    PasswordChangeRequestSerializer,
    PasswordResetEmailSendSerializer,
    PasswordResetVerifyCodeSerializer,
)


# 이메일 찾기
class EmailFindView(APIView):
    @extend_schema(
        request=EmailFindRequestSerializer,
        responses={200: EmailFindResponseSerializer},
        description="(Mock) 이메일 찾기 API - 이름과 휴대폰 번호로 인증 후 마스킹해서 이메일 반환",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = EmailFindRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        phone_number = serializer.validated_data["phone_number"]

        if name == "홍길동" and phone_number == "01012345678":
            return Response({"email": "ho***@example.com"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "일치하는 계정을 찾을 수 없습니다. 이름과 휴대폰 번호를 확인해주세요."},
            status=status.HTTP_404_NOT_FOUND,
        )


# 비밀번호 재설정 하기위한 인증코드 발송
class PasswordResetEmailSendView(APIView):
    @extend_schema(
        request=PasswordResetEmailSendSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="(Mock) 비밀번호 재설정 - 인증코드 이메일 발송",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetEmailSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        if email == "user@example.com":
            return Response(
                {"message": "인증코드가 이메일로 발송되었습니다."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "해당 이메일로 등록된 계정이 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )


# 비밀번호 재설정 -> 인증코드 확인
class PasswordResetVerifyCodeView(APIView):
    @extend_schema(
        request=PasswordResetVerifyCodeSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="(Mock) 비밀번호 재설정 - 인증코드 검증",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        if code == "123456":
            return Response(
                {"message": "이메일 인증이 완료되었습니다."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "인증코드가 올바르지 않거나 만료되었습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# 비밀번호 변경
class PasswordChangeView(APIView):
    @extend_schema(
        request=PasswordChangeRequestSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="(Mock) 비밀번호 변경 API",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "message": "비밀번호 변경에 성공했습니다. 잠시 후 로그인 페이지로 이동합니다.",
                "redirect_in_seconds": 10,
            },
            status=status.HTTP_200_OK,
        )
