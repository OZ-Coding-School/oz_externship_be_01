from rest_framework import serializers


class BasePaginationSerializer(serializers.Serializer[dict]):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)