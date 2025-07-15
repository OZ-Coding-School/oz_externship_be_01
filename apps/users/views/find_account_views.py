from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.models.social_user import SocialUser
from apps.users.serializers.find_account_serializers import (
    EmailFindRequestSerializer,
    EmailFindResponseSerializer,
    PasswordChangeRequestSerializer,
    PasswordResetEmailSendSerializer,
    PasswordResetVerifyCodeSerializer,
)
from apps.users.tasks import send_verification_email_task
from apps.users.utils.email_masking_utils import mask_email
from apps.users.utils.redis_utils import (
    get_reset_email_code,
    is_email_find_phone_verified,
    is_phone_verified,
    mark_reset_email_as_verified,
    store_reset_email_code,
)
from core.utils.base62 import generate_base62_code


# 이메일 찾기
class EmailFindView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailFindRequestSerializer,
        responses={200: EmailFindResponseSerializer},
        description="이메일 찾기 API - 이름과 휴대폰 번호로 인증 후 마스킹해서 이메일 반환",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = EmailFindRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        phone_number = serializer.validated_data["phone_number"]

        if not is_email_find_phone_verified(phone_number):
            return Response({"message": "휴대폰 인증을 먼저 완료해주세요."}, status=400)

        try:
            user = User.objects.get(name=name, phone_number=phone_number)
            return Response({"email": mask_email(user.email)}, status=200)
        except User.DoesNotExist:
            return Response(
                {"message": "일치하는 계정을 찾을 수 없습니다. 이름과 휴대폰 번호를 확인해주세요."},
                status=404,
            )


# 비밀번호 재설정 하기위한 인증코드 발송
class PasswordResetEmailSendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetEmailSendSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="비밀번호 재설정 - 인증코드 이메일 발송",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetEmailSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "해당 이메일로 등록된 계정이 없습니다."}, status=404)

        if SocialUser.objects.filter(user=user).exists():
            return Response({"message": "소셜 로그인 유저는 비밀번호를 재설정할 수 없습니다."}, status=400)
        code = generate_base62_code()
        store_reset_email_code(email, code)
        send_verification_email_task.delay(email=email, code=code)

        return Response({"message": "인증코드가 이메일로 발송되었습니다."}, status=200)


# 비밀번호 재설정 -> 인증코드 확인
class PasswordResetVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetVerifyCodeSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="비밀번호 재설정 - 인증코드 검증",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResetVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        input_code = serializer.validated_data["code"]

        saved_code = get_reset_email_code(email)
        if saved_code and input_code == saved_code:
            mark_reset_email_as_verified(email)
            return Response({"message": "이메일 인증이 완료되었습니다."}, status=200)
        return Response({"message": "인증코드가 올바르지 않거나 만료되었습니다."}, status=400)


# 비밀번호 변경
class PasswordChangeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordChangeRequestSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="비밀번호 변경 API",
        tags=["account-find"],
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save(update_fields=["password"])
            return Response(
                {
                    "message": "비밀번호 변경에 성공했습니다.",
                    "redirect_in_seconds": 10,
                },
                status=200,
            )
        except User.DoesNotExist:
            return Response({"message": "해당 이메일 계정을 찾을 수 없습니다."}, status=404)
