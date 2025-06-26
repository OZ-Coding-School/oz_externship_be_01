from datetime import datetime, timedelta

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.models.withdrawals import Withdrawal
from apps.users.serializers.withdrawal_serializers import (
    UserDeleteSerializer,
    UserRestoreSerializer,
)


# 회원탈퇴
class UserDeleteView(APIView):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserDeleteSerializer,
        description="(Mock) 회원 탈퇴 API - 실제 DB 저장 없이 더미 유저 반환",
        tags=["withdrawal"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            dummy_user = User(
                id=1,
                email="withdrawn@example.com",
                nickname="탈퇴 유저",
                is_active=False,
            )

            dummy_withdrawal = Withdrawal(
                user=dummy_user,
                reason=serializer.validated_data["reason"],
                reason_detail=serializer.validated_data["detail"],
                due_date=datetime.now().date() + timedelta(days=14),
            )

            return Response(
                {
                    "message": "더미 유저 탈퇴 완료",
                    "email": dummy_user.email,
                    "탈퇴사유": dummy_withdrawal.reason,
                    "상세사유": dummy_withdrawal.reason_detail,
                    "삭제예정일": dummy_withdrawal.due_date,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRestoreView(APIView):
    serializer_class = UserRestoreSerializer

    @extend_schema(
        request=UserRestoreSerializer,
        description="(Mock) 탈퇴 계정 복구 API - 실제 DB 저장 없이 더미 유저 반환",
        tags=["withdrawal"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            verification_code = serializer.validated_data["verification_code"]

            if verification_code == "123456":
                dummy_user = User(
                    id=2,
                    email=email,
                    nickname="복구유저",
                    is_active=True,
                )

                return Response(
                    {
                        "message": "더미 계정 복구 완료",
                        "email": dummy_user.email,
                        "nickname": dummy_user.nickname,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response({"error": "더미 인증 실패"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
