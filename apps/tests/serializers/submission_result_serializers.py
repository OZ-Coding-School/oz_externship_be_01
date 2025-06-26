# 쪽지 시험 결과 조회
from rest_framework import serializers

from apps.tests.models import Test, TestDeployment, TestQuestion, TestSubmission


class TestSerializer(serializers.ModelSerializer[Test]):
    class Meta:
        model = Test
        fields = ["id", "title", "thumbnail_img_url"]


class TestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = TestSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = [
            "id",
            "test",
            "questions_snapshot_json",
        ]


class TestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = TestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ["id", "deployment", "cheating_count", "answers_json"]
