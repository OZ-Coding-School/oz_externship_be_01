from rest_framework import serializers

from apps.users.models.user import User
from apps.users.models.withdrawals import Withdrawal


class AdminWithdrawalRestoreSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        user_id = data.get("user_id")
        if not User.objects.filter(id=user_id, is_active=False).exists():
            raise serializers.ValidationError("해당 탈퇴 사용자를 찾을 수 없습니다.")
        return data

    def restore_user(self):
        user_id = self.validated_data["user_id"]
        try:
            user = User.objects.get(id=user_id)
            Withdrawal.objects.filter(user_id=user_id).update(user=None)
            user.is_active = True
            user.save()
            return {"message": "사용자 계정이 성공적으로 복구되었습니다."}

        except Exception as e:
            raise serializers.ValidationError(f"복구 실패: {str(e)}")
