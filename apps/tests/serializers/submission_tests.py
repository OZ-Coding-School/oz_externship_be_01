# 쪽지 시험 응시, 제출, 결과 조회
from rest_framework import serializers


# 쪽지 시험 질문
class QuestionSerializer(serializers.Serializer):  # type: ignore
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), required=False)
    point = serializers.IntegerField()
    prompt = serializers.CharField(required=False, allow_null=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    student_answer = serializers.ListField(child=serializers.CharField(), required=False)
    correct_answer = serializers.ListField(child=serializers.CharField(), required=False)
    explanation = serializers.CharField(required=False)
    is_correct = serializers.BooleanField(required=False)


# 쪽지 시험 응시
class TestStartSerializer(serializers.Serializer):  # type: ignore
    test_id = serializers.IntegerField()
    access_code = serializers.CharField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField()
    elapsed_time = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    questions = QuestionSerializer(many=True)


# 쪽지 시험 제출
class SubmissionSubmitSerializer(serializers.Serializer):  # type: ignore
    submission_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    deployment_id = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    cheating_count = serializers.IntegerField()
    answers = serializers.ListField(child=serializers.DictField())


# 쪽지 시험 결과 조회
class TestResultSerializer(serializers.Serializer):  # type: ignore
    submission_id = serializers.IntegerField()
    test_title = serializers.CharField()
    test_thumbnail_img_url = serializers.CharField()
    total_questions = serializers.IntegerField()
    questions = QuestionSerializer(many=True)
    cheating_count = serializers.IntegerField()
