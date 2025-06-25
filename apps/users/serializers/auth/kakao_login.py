from rest_framework import serializers
from typing import Any

class KakaoLoginSerializer(serializers.Serializer[Any]):
    access_token = serializers.CharField()