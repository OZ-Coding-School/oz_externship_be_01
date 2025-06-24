from rest_framework import serializers


class TestQuestionSerializer(serializers.Serializer):  # type: ignore
    id = serializers.IntegerField(read_only=True)
    test_id = serializers.IntegerField()
    content = serializers.CharField()
    answer = serializers.CharField()
