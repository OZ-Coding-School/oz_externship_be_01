from rest_framework import serializers
from typing import Any

class NaverLoginSerializer(serializers.Serializer[Any]):
    access_token = serializers.CharField()