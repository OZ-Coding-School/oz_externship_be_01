from datetime import date, timedelta

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.models.withdrawals import Withdrawal
from apps.users.serializers.withdrawal_serializers import (
    UserDeleteSerializer,
    UserRestoreSerializer,
)
from apps.users.utils.redis_utils import is_email_verified


# 회원탈퇴
class UserDeleteView(APIView):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserDeleteSerializer,
        description="회원 탈퇴 API - 회원탈퇴",
        tags=["user-withdrawal"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            reason = serializer.validated_data["reason"]
            detail = serializer.validated_data["detail"]

            # 탈퇴 유예기간 14일 후 삭제 예정
            due_date = timezone.now().date() + timedelta(days=14)

            assert isinstance(user, User)

            # Withdrawal 기록 생성
            Withdrawal.objects.create(
                user=user,
                reason=reason,
                reason_detail=detail,
                due_date=due_date,
            )

            # 유저 비활성화 및 탈퇴 처리
            user.is_active = False
            user.save(update_fields=["is_active"])
            assert isinstance(user, User)

            return Response(
                {
                    "message": "회원 탈퇴 완료",
                    "email": user.email,
                    "탈퇴사유": reason,
                    "상세사유": detail,
                    "삭제예정일": due_date,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 회원복구
class UserRestoreView(APIView):
    serializer_class = UserRestoreSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRestoreSerializer,
        description="탈퇴 계정 복구 API - 이메일 인증 후 복구 가능",
        tags=["user-restore"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            if not is_email_verified(email):
                return Response(
                    {"error": "이메일 인증이 완료되지 않았습니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                user = User.objects.get(email=email, is_active=False)
            except User.DoesNotExist:
                return Response(
                    {"error": "비활성화된 계정을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                withdrawal = Withdrawal.objects.get(user=user)
            except Withdrawal.DoesNotExist:
                return Response(
                    {"error": "탈퇴 정보가 존재하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if withdrawal.due_date <= date.today():
                return Response(
                    {"error": "계정 복구 가능 기간(14일)이 지났습니다."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            user.is_active = True
            user.save(update_fields=["is_active"])
            withdrawal.delete()  # 복구 시 탈퇴 기록 삭제

            return Response(
                {
                    "message": "회원 복구 완료",
                    "email": user.email,
                    "nickname": user.nickname,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
