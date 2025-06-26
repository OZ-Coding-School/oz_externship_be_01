# 쪽지 시험 응시 내역 상세 조회 및 삭제
from rest_framework import serializers

from apps.courses.models import Course, Generation, Subject, User
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.users.models.permissions import PermissionsStudent


class UserSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = User
        fields = ["id", "name", "nickname"]


class StudentSerializer(serializers.ModelSerializer):  # type: ignore
    user = UserSerializer(read_only=True)

    class Meta:
        model = PermissionsStudent
        fields = ["id", "user"]


class CourseSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = Course
        fields = ["id", "name"]


class GenerationSerializer(serializers.ModelSerializer):  # type: ignore
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ["id", "course", "number"]


class SubjectSerializer(serializers.ModelSerializer):  # type: ignore

    class Meta:
        model = Subject
        fields = ["id", "title"]


class TestSerializer(serializers.ModelSerializer):  # type: ignore
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ["id", "subject", "title", "created_at", "updated_at"]


class TestDeploymentSerializer(serializers.ModelSerializer):  # type: ignore
    test = TestSerializer(read_only=True)
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = ["id", "test", "generation", "duration_time", "open_at", "close_at", "questions_snapshot_json"]


class TestDetailSerializer(serializers.ModelSerializer):  # type: ignore
    deployment = TestDeploymentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ["id", "deployment", "student", "cheating_count", "started_at", "answers_json"]
