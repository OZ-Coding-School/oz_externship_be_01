from rest_framework import serializers

from apps.users.models import User
from apps.users.models.withdrawals import Withdrawal


# 회원 탈퇴 응답 시리얼라이저
class WithdrawalResponseSerializer(serializers.ModelSerializer[Withdrawal]):
    class Meta:
        model = Withdrawal
        fields = ["id", "user", "reason", "reason_detail", "due_date", "created_at"]
