from datetime import date
from typing import Any, Dict

from rest_framework import serializers
from rest_framework.permissions import AllowAny

from apps.courses.models import Course, Generation


# 기수 등록
class GenerationCreateSerializer(serializers.ModelSerializer[Generation]):
    course = serializers.IntegerField()

    class Meta:
        model = Generation
        fields = [
            "id",
            "course",
            "number",
            "max_student",
            "start_date",
            "end_date",
            "status",
        ]

        read_only_fields = ("id",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError("종료일은 시작일 이후여야 합니다.")
        return attrs


# 기수 목록
class GenerationListSerializer(serializers.ModelSerializer[Generation]):
    course_name = serializers.CharField(source="course.name", read_only=True)
    registered_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "course",
            "course_name",
            "number",
            "max_student",
            "registered_students",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "course",
            "course_name",
            "registered_students",
            "created_at",
            "updated_at",
        ]


# 기수 상세 조회
class GenerationDetailSerializer(serializers.ModelSerializer[Generation]):
    course_name = serializers.CharField(source="course.name", read_only=True)
    course_tag = serializers.CharField(source="course.tag", read_only=True)
    course_description = serializers.CharField(source="course.description", read_only=True)
    registered_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "course",
            "course_name",
            "course_tag",
            "course_description",
            "number",
            "registered_students",
            "max_student",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# 기수 수정
class GenerationUpdateSerializer(serializers.ModelSerializer[Generation]):

    class Meta:
        model = Generation
        fields = [
            "start_date",
            "end_date",
        ]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and start > end:
            raise serializers.ValidationError("종료일은 시작일 이후여야 합니다.")
        return attrs


# 과정 - 기수 대시보드
class CourseTrendSerializer(serializers.Serializer[Any]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    labels = serializers.ListField(child=serializers.CharField())
    registered_students_count = serializers.ListField(child=serializers.IntegerField())


# 월별
class MonthlyCourseSerializer(serializers.Serializer[Any]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)

    labels = serializers.ListField(child=serializers.CharField())
    monthly_count = serializers.ListField(child=serializers.IntegerField())
