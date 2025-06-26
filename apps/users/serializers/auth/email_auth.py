from typing import Any

from rest_framework.serializers import CharField, EmailField, Serializer


class EmailSendCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()


class EmailVerifyCodeSerializer(Serializer[Any]):
    email: EmailField = EmailField()
    code: CharField = CharField()
