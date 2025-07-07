from typing import Any

from rest_framework import serializers

# 회원탈퇴 및 회원 복구 API


class UserDeleteSerializer(serializers.Serializer[Any]):
    reason = serializers.CharField(max_length=255)
    detail = serializers.CharField()


class UserDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()
    reason = serializers.CharField()
    reason_detail = serializers.CharField()
    due_date = serializers.DateField()


class UserRestoreSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()



class UserRestoreResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()
    nickname = serializers.CharField()
