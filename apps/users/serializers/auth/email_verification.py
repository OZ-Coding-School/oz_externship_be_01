from typing import Any

from rest_framework import serializers


class EmailVerificationSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
