from rest_framework import serializers
from apps.courses.models import Course, Generation
from apps.users.models.user import User
from apps.users.models.student_enrollment import StudentEnrollmentRequest


class SimpleUserSerializer(serializers.ModelSerializer):
    """간단한 사용자 정보 serializer"""

    class Meta:
        model = User
        fields = ["id", "name", "email"]


class EnrollmentRequestSerializer(serializers.ModelSerializer):
    """수강 등록 요청 serializer"""

    user = SimpleUserSerializer(read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    generation_number = serializers.IntegerField(source="generation.number", read_only=True)

    class Meta:
        model = StudentEnrollmentRequest
        fields = ["id", "user", "user_name", "user_email", "generation_number", "status", "created_at", "accepted_at"]
        read_only_fields = ["id", "created_at", "accepted_at"]


class CourseEnrollmentStatsSerializer(serializers.Serializer):
    """과정별 수강 등록 통계 serializer"""

    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    total_enrollments = serializers.IntegerField()
    pending_enrollments = serializers.IntegerField()
    approved_enrollments = serializers.IntegerField()
    rejected_enrollments = serializers.IntegerField()
    generations = serializers.ListField(child=serializers.DictField(), help_text="과정별 기수별 등록 현황")


class CourseEnrollmentListSerializer(serializers.Serializer):
    """과정별 수강 등록 목록 serializer"""

    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    enrollments = EnrollmentRequestSerializer(many=True)


class CourseListSerializer(serializers.ModelSerializer):
    """과정 목록 조회용 serializer"""

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CourseSerializer(serializers.ModelSerializer):
    """과정 등록/수정/상세 조회용 serializer"""

    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
            "student_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count"]

    def get_student_count(self, course):
        return StudentEnrollmentRequest.objects.filter(generation__course=course, status="APPROVED").count()
