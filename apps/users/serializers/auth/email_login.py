from typing import Any

from rest_framework import serializers


class EmailLoginSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField()
