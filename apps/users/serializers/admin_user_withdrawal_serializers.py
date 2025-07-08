from rest_framework import serializers

from apps.users.models.withdrawals import Withdrawal


# 회원 탈퇴 응답 시리얼라이저
class WithdrawalResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Withdrawal  # 직렬화할 모델 지정
        fields = ["id", "user_id", "reason", "reason_detail", "due_date", "created_at"]


class AdminListWithdrawalSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    name = serializers.CharField(source="user.name")
    role = serializers.CharField(source="user.role")
    brith_date = serializers.DateField(source="user.brith_date")

    class Meta:
        Model = Withdrawal
        fields = ["id", "email", "name", "role", "brith_date", "reason", "reason_detail", "due_date", "created_at"]
