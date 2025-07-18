from datetime import date, timedelta
from typing import Any, Dict

from rest_framework import serializers
from rest_framework.permissions import AllowAny

from apps.courses.models import Course, Generation


# 기수 등록
class GenerationCreateSerializer(serializers.ModelSerializer[Generation]):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),  # 유효성 검사를 위해 모든 Course 객체를 쿼리셋으로 넘겨줌
        source="course",  # 클라이언트로부터 'course_id'를 받아서 모델의 'course' 필드에 매핑
        write_only=True,  # 입력 전용 필드
        help_text="등록할 과정의 고유 ID",
    )
    status = serializers.ChoiceField(
        choices=Generation.GenStatus.choices,
        help_text="기수 상태 (Ready, Ongoing, Finished 중 선택)",
    )

    class Meta:
        model = Generation
        fields = [
            "id",
            "course_id",
            "number",
            "max_student",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError("종료일은 시작일 이후여야 합니다.")

        max_student = attrs.get("max_student")
        if max_student is not None and (max_student < 1 or max_student > 60):
            raise serializers.ValidationError(
                {"max_student": "최대 등록 인원(max_student)은 1 이상 60 이하여야 합니다."}
            )

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Generation:
        # validated_data에는 이제 'course_id' 대신 'course' 키로 Course 객체의 ID가 들어있음

        course_instance = validated_data.pop("course")  # source='course'로 들어온 ID 값

        # Generation 객체 생성 (course와 status 필드 추가)
        generation = Generation.objects.create(course=course_instance, **validated_data)
        return generation


# 기수 목록
class GenerationListSerializer(serializers.ModelSerializer[Generation]):
    course_name = serializers.CharField(source="course.name", read_only=True)
    course_tag = serializers.CharField(source="course.tag", read_only=True)
    registered_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "course_name",
            "course_tag",
            "number",
            "max_student",
            "registered_students",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


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
        extra_kwargs = {
            "start_date": {"required": False},
            "end_date": {"required": False},
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if "start_date" not in attrs and "end_date" not in attrs:
            raise serializers.ValidationError("수강 시작일과 종료일 중 최소 하나는 제공되어야 합니다.")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("수강 종료일은 수강 시작일 이후여야 합니다.")

        if start_date and end_date:
            duration = end_date - start_date  # timedelta 객체 반환

        if duration < timedelta(days=7):
            raise serializers.ValidationError("수강 기간은 최소 7일 이상이어야 합니다.")

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
