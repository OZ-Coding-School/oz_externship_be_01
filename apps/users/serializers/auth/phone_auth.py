from rest_framework import serializers
from apps.users.models import User
from apps.users.utils.redis import (
    get_stored_phone_code,
    mark_phone_as_verified,
)


class PhoneSendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)


class PhoneVerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone_number")
        code = data.get("code")

        # 유저 존재 확인
        if not User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("해당 전화번호의 유저가 존재하지 않습니다.")

        # Redis에서 코드 조회
        stored_code = get_stored_phone_code(phone)
        if not stored_code:
            raise serializers.ValidationError("인증코드가 존재하지 않거나 만료되었습니다.")
        if stored_code != code:
            raise serializers.ValidationError("인증코드가 일치하지 않습니다.")

        # 인증 성공 시 인증 완료 상태 저장 (선택)
        mark_phone_as_verified(phone)

        return data