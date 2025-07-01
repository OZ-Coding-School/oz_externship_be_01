from rest_framework import serializers

from apps.courses.models import Course, Generation
from apps.tests.models import TestDeployment
from apps.tests.serializers.test_serializers import (
    AdminListSerializer,
    AdminTestSerializer,
    UserTestSerializer,
)


# 공통 User&Admin
class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("id", "name")


# 공통 User&Admin
class GenerationSerializer(serializers.ModelSerializer[Generation]):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("id", "course", "number")


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListCourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("name",)


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListGenerationSerializer(serializers.ModelSerializer[Generation]):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("course", "number")


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


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestListDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminListSerializer(read_only=True)
    generation_number = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation_number",
        )


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = UserTestSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "duration_time",
            "questions_snapshot_json",
        )


# 사용자 쪽지 시험 응시: 요청, access_code 검증용
class UserTestStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestDeployment
        fields = ("access_code",)
        extra_kwargs = {
            "access_code": {"write_only": True},
        }
