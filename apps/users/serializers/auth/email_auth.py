from typing import Any

from rest_framework import serializers
from rest_framework.serializers import CharField, EmailField, Serializer

from apps.users.utils.redis import get_stored_email_code


class EmailSendCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()


class EmailVerifyCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()
    verification_code: CharField = CharField()

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        email = data["email"]
        code = data["verification_code"]

        stored_code = get_stored_email_code(email)
        if stored_code is None:
            raise serializers.ValidationError("인증 코드가 만료되었거나 존재하지 않습니다.")

        if code != stored_code:
            raise serializers.ValidationError("인증 코드가 일치하지 않습니다.")

        return data
