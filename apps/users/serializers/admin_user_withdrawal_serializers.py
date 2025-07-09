from rest_framework import serializers

from apps.users.models.withdrawals import Withdrawal


# 회원 탈퇴 응답 시리얼라이저
class WithdrawalResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Withdrawal  # 직렬화할 모델 지정
        fields = ["id", "user_id", "reason", "reason_detail", "due_date", "created_at"]


class WithdrawalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "role", "birthday"]


class AdminListWithdrawalSerializer(serializers.ModelSerializer):
    user = WithdrawalUserSerializer()

    class Meta:
        model = Withdrawal
        fields = ["id", "user", "reason", "reason_detail", "due_date", "created_at"]
