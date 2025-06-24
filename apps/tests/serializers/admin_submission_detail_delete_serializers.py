# 쪽지 시험 응시 내역 상세 조회 및 삭제
from rest_framework import serializers


class StudentSerializer(serializers.Serializer):  # type: ignore
    nickname = serializers.CharField()
    name = serializers.CharField()
    generation = serializers.CharField()


class AnswerSerializer(serializers.Serializer):  # type: ignore
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    point = serializers.IntegerField()
    correct_answer = serializers.CharField()
    student_answer = serializers.CharField()
    is_correct = serializers.BooleanField()


class SubmissionDetailSerializer(serializers.Serializer):  # type: ignore
    submission_id = serializers.IntegerField()
    test_title = serializers.CharField()
    subject_title = serializers.CharField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    student = StudentSerializer()
    score = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    submitted_at = serializers.DateTimeField()
    answers = AnswerSerializer(many=True)
