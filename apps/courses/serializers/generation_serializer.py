from datetime import date
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

        extra_kwargs = {
            "status": {"read_only": True},
        }

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

        course_id_from_input = attrs.get("course")
        if course_id_from_input:
            try:
                Course.objects.get(id=course_id_from_input)
            except Course.DoesNotExist:
                raise serializers.ValidationError({"course_id": "해당 course_id를 가진 과정이 존재하지 않습니다."})

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Generation:
        # validated_data에는 이제 'course_id' 대신 'course' 키로 Course 객체의 ID가 들어있음

        course_instance = validated_data.pop("course")  # source='course'로 들어온 ID 값

        # 기수 상태 자동 계산
        start_date = validated_data.get("start_date")
        end_date = validated_data.get("end_date")
        calculated_status = self._calculate_cohort_status(start_date, end_date)

        # validated_data에서 'status' 필드를 명시적으로 제거 (혹시 모를 중복 전달 방지)
        validated_data.pop("status", None)

        # Generation 객체 생성 (course와 status 필드 추가)
        generation = Generation.objects.create(course=course_instance, status=calculated_status, **validated_data)
        return generation

    def _calculate_cohort_status(self, start_date, end_date) -> str:
        today = date.today()
        if today > start_date:
            return "Ready"
        elif start_date <= today <= end_date:
            return "Ongoing"
        else:
            return "Finished"


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
