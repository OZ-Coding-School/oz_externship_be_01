from typing import Any

from rest_framework import serializers
from rest_framework.serializers import Serializer


class PhoneSendCodeSerializer(Serializer[Any]):
    phone_number = serializers.CharField()


class PhoneVerifyCodeSerializer(Serializer[Any]):
    phone_number = serializers.CharField()
    code = serializers.CharField()
