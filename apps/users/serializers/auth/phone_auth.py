from rest_framework import serializers

from apps.users.utils.twilio_utils import (
    check_verification_code,
    normalize_phone_number,
)


class SendPhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class VerifyPhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")
        phone = normalize_phone_number(phone)
        result = check_verification_code(phone_number=phone, code=code)
        if not result:
            raise serializers.ValidationError("invalid verification code.")

        return attrs
