from rest_framework import serializers
from typing import Any

class PhoneVerificationSerializer(serializers.Serializer[Any]):
    phone = serializers.CharField()