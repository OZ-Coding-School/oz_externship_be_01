from typing import Any

from rest_framework import serializers

# 회원탈퇴 및 회원 복구 API

class UserDeleteSerializer(serializers.Serializer[Any]):
    reason = serializers.CharField(max_length=255)
    detail = serializers.CharField()


class UserRestoreSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    verification_code = serializers.CharField()
