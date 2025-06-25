from typing import Any

from rest_framework import serializers


class KakaoLoginSerializer(serializers.Serializer[Any]):
    access_token = serializers.CharField()
