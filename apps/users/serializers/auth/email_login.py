from typing import Any

from rest_framework import serializers
from rest_framework.serializers import Serializer


class EmailLoginSerializer(Serializer[Any]):
    email = serializers.EmailField()
    code = serializers.CharField()
