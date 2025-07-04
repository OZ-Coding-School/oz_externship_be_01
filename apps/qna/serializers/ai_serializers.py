from rest_framework import serializers


class AIRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)


class AIResponseSerializer(serializers.Serializer):
    response = serializers.CharField()


class MenuClickSerializer(serializers.Serializer):
    menu = serializers.CharField()
    submenu = serializers.CharField(required=False)
