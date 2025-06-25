from rest_framework import serializers
from typing import Any

class EmailLoginSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField()