from typing import Any

from rest_framework import serializers


class SignupSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirm = serializers.CharField()
    name = serializers.CharField()
    nickname = serializers.CharField()
    phone = serializers.CharField()
    birth_date = serializers.DateField()
    profile_image = serializers.CharField(required=False, allow_blank=True)
