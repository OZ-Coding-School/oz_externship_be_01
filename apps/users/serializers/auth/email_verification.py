from rest_framework import serializers
from typing import Any

class EmailVerificationSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()