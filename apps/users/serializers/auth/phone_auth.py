from rest_framework import serializers


class SendPhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class VerifyPhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
