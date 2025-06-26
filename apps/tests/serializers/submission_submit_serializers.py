# 쪽지 시험 제출
from rest_framework import serializers

from apps.tests.models import TestSubmission


class TestSubmitSerializer(serializers.ModelSerializer[TestSubmission]):

    class Meta:
        model = TestSubmission
        fields = [
            "id",
            # "student_id",
            "deployment",
            "started_at",
            "cheating_count",
            "answers_json",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            # "student_id",
            "deployment",
            "started_at",
            "cheating_count",
            "created_at",
            "updated_at",
        ]
