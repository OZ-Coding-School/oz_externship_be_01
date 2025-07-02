from typing import Any, Dict

from rest_framework import serializers
from django.utils import timezone
from apps.users.models import User, PhoneVerificationCode

class PhoneSendCodeSerializer(serializers.Serializer):
    # 인증 코드 전송 요청을 처리하는 시리얼라이저
    phone_number = serializers.CharField(max_length=20)


class PhoneVerifyCodeSerializer(serializers.Serializer):
    # 인증 코드 유효성을 검증하는 시리얼라이저

    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        phone: str = data.get("phone_number")
        code: str = data.get("code")

        # 입력된 전화번호에 해당하는 유저가 존재하는지 확인
        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("해당 전화번호의 유저가 존재하지 않습니다.")

        # 해당 유저와 코드로 가장 최근에 생성된 인증 코드 검색
        try:
            verification = PhoneVerificationCode.objects.filter(
                user=user, code=code
            ).latest("created_at")
        except PhoneVerificationCode.DoesNotExist:
            raise serializers.ValidationError("인증코드가 일치하지 않습니다.")

        # 인증 코드가 만료되었는지 검사
        if verification.expires_at < timezone.now():
            raise serializers.ValidationError("인증코드가 만료되었습니다.")
        return data
