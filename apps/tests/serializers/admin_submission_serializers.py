# 쪽지 시험 응시 내역 목록 조회
from rest_framework import serializers

from apps.courses.models import Course, Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission


class UserSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = User
        fields = ["id", "name", "nickname"]


class GenerationSerializer(serializers.ModelSerializer):  # type: ignore
    user = UserSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ["id", "course", "number"]


class SubjectSerializer(serializers.ModelSerializer):  # type: ignore
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "title"]


class TestSerializer(serializers.ModelSerializer):  # type: ignore
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ["id", "subject", "title"]


class TestDeploymentSerializer(serializers.ModelSerializer):  # type: ignore
    test = TestSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = ["id", "generation"]


class TestStartSerializer(serializers.ModelSerializer):  # type: ignore
    deployment = TestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = [
            "id",
            # "student",
            "cheating_count",
            "started_at",
        ]
