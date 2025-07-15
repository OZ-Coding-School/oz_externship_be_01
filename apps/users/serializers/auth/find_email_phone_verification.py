from rest_framework import serializers

from apps.users.utils.redis_utils import mark_email_find_phone_as_verified
from apps.users.utils.twilio_utils import (
    check_verification_code,
    normalize_phone_number,
)


class SendPhoneCodeForEmailSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class VerifyPhoneCodeForEmailFindSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone = attrs.get("phone")
        code = attrs.get("code")

        normalized_phone = normalize_phone_number(phone)

        status = check_verification_code(phone_number=normalized_phone, code=code)
        if status != "approved":
            raise serializers.ValidationError("인증번호가 올바르지 않습니다.")
        mark_email_find_phone_as_verified(phone)
        return attrs
