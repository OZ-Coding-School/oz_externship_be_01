# 쪽지 시험 응시 내역 상세 조회 및 삭제
from rest_framework import serializers

from apps.courses.models import Generation, Subject
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.tests.serializers.admin_submission_serializers import (
    CourseSerializer,
    StudentSerializer,
)


class GenerationSerializer(serializers.ModelSerializer[Generation]):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ["id", "course", "number"]


class SubjectSerializer(serializers.ModelSerializer[Subject]):

    class Meta:
        model = Subject
        fields = ["id", "title"]


class TestSerializer(serializers.ModelSerializer[Test]):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ["id", "subject", "title", "created_at", "updated_at"]


class TestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = TestSerializer(read_only=True)
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = ["id", "test", "generation", "duration_time", "open_at", "close_at", "questions_snapshot_json"]


class TestDetailSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = TestDeploymentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ["id", "deployment", "student", "cheating_count", "started_at", "answers_json"]
