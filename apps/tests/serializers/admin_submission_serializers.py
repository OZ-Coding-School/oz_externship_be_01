# 쪽지 시험 응시 내역 목록 조회
from rest_framework import serializers


class StudentSerializer(serializers.Serializer):  # type: ignore
    nickname = serializers.CharField()
    name = serializers.CharField()
    generation = serializers.CharField()


class TestInfoSerializer(serializers.Serializer):  # type: ignore
    title = serializers.CharField()
    subject_title = serializers.CharField()


class SubmissionSerializer(serializers.Serializer):  # type: ignore
    submission_id = serializers.IntegerField()
    student = StudentSerializer()
    test = TestInfoSerializer()
    score = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    submitted_at = serializers.DateTimeField()


class SubmissionListResponseSerializer(serializers.Serializer):  # type: ignore
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = SubmissionSerializer(many=True)
