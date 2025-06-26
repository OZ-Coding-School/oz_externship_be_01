from typing import Any

from rest_framework import serializers
from rest_framework.serializers import Serializer


class SocialLoginSerializer(Serializer[Any]):
    access_token = serializers.CharField()
