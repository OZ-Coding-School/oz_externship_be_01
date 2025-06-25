from typing import Any

from rest_framework import serializers


class PhoneVerificationSerializer(serializers.Serializer[Any]):
    phone = serializers.CharField()
