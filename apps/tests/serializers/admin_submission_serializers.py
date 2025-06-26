# 쪽지 시험 응시 내역 전체 목록 조회
from rest_framework import serializers

from apps.courses.models import Course, Generation, Subject
from apps.tests.models import Test, TestDeployment, TestSubmission
from apps.users.models import PermissionsStudent, User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "name", "nickname"]


class StudentSerializer(serializers.ModelSerializer[PermissionsStudent]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PermissionsStudent
        fields = ["id", "user"]


class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name"]


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
        fields = ["id", "subject", "title"]


class TestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = TestSerializer(read_only=True)
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = ["id", "test", "generation"]


class TestListSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = TestDeploymentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = [
            "id",
            "deployment",
            "student",
            "cheating_count",
            "started_at",
        ]
