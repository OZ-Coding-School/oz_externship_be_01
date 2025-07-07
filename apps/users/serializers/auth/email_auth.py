from typing import Any

from rest_framework import serializers
from rest_framework.serializers import CharField, EmailField, Serializer

from apps.users.utils.redis_utils import (
    get_signup_email_code,
    get_restore_email_code,
)


class EmailSendCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()
    purpose = serializers.ChoiceField(choices=["signup", "restore"])


class EmailVerifyCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()
    verification_code: CharField = CharField()
    purpose: CharField = serializers.ChoiceField(choices=["signup", "restore"])

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        email = data["email"]
        code = data["verification_code"]
        purpose = data["purpose"]

        if purpose == "signup":
            stored_code = get_signup_email_code(email)
        elif purpose == "restore":
            stored_code = get_restore_email_code(email)
        else:
            raise serializers.ValidationError("잘못된 목적입니다.")

        if stored_code is None:
            raise serializers.ValidationError("인증 코드가 만료되었거나 존재하지 않습니다.")

        if code != stored_code:
            raise serializers.ValidationError("인증 코드가 일치하지 않습니다.")

        return data
