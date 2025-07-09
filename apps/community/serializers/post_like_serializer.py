from rest_framework import serializers


class PostLikeResponseSerializer(serializers.Serializer):
    liked = serializers.BooleanField()
