from django.utils import timezone
from rest_framework import serializers

from apps.users.models import PhoneVerificationCode


class PhoneSendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)


class PhoneVerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone_number")
        code = data.get("code")

        try:
            verification = PhoneVerificationCode.objects.filter(phone_number=phone, code=code).latest("created_at")
        except PhoneVerificationCode.DoesNotExist:
            raise serializers.ValidationError("인증코드가 일치하지 않습니다.")

        if verification.expires_at < timezone.now():
            raise serializers.ValidationError("인증코드가 만료되었습니다.")

        return data
