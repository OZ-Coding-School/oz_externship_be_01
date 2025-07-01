from datetime import datetime, timedelta

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.serializers.questions_serializers import QuestionCreateSerializer
from apps.users.models.user import User
from apps.users.models.withdrawals import Withdrawal
from apps.users.serializers.admin_user_withdrawal_serializers import (
    WithdrawalResponseSerializer,
)


# 어드민 회원 탈퇴 상세조회
class AdminDetailWithdrawalView(APIView):
    permission_classes = [AllowAny]
    serializer_class = WithdrawalResponseSerializer

    @extend_schema(tags=["Admin - 회원 관리"], summary="어드민 회원 탈퇴 상세 조회")
    def get(self, request: Request, withdrawal_id: int) -> Response:
        try:
            withdrawal = Withdrawal.objects.select_related("user").get(id=withdrawal_id)
        except Withdrawal.DoesNotExist:
            return Response({"detail": "탈퇴 내역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WithdrawalResponseSerializer(withdrawal)
        return Response(serializer.data, status=status.HTTP_200_OK)
