from rest_framework import serializers

from apps.courses.models import Course, Generation
from apps.tests.models import TestDeployment
from apps.tests.serializers.test_serializers import (
    AdminTestSerializer,
    UserTestSerializer,
)


# 공통 Admin&User
class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("id", "name")


# 공통 Admin&User
class GenerationSerializer(serializers.ModelSerializer[Generation]):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("id", "course", "number")


# 공통 AdminTestDeploymentSerializer
class AdminTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestSerializer(read_only=True)
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
            "questions_snapshot_json",
        )


# 공통 UserTestDeploymentSerializer
class UserTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = UserTestSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "generation",
            "duration_time",
            "access_code",  # 읽기 전용
            "open_at",
            "close_at",
            "questions_snapshot_json",
            "status",
            "created_at",
            "updated_at",
        )


# 사용자 쪽지 시험 응시
class UserTestStartSerializer(serializers.ModelSerializer[TestDeployment]):
    deployment = UserTestDeploymentSerializer(read_only=True)
    access_code = serializers.CharField(write_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "deployment",
            "access_code",  # 입력 전용
        )
        read_only_fields = (
            "id",
            "deployment",
            "access_code",
        )
