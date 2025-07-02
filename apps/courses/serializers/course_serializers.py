from rest_framework import serializers
from apps.courses.models import Course, Generation
from apps.users.models.user import User
from apps.users.models.student_enrollment import StudentEnrollmentRequest


# 사용자 간단 정보
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']


# 수강 등록 요청
class EnrollmentRequestSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    generation_number = serializers.IntegerField(source='generation.number', read_only=True)

    class Meta:
        model = StudentEnrollmentRequest
        fields = [
            'id', 'user', 'user_name', 'user_email', 'generation_number',
            'status', 'created_at', 'accepted_at'
        ]
        read_only_fields = ['id', 'created_at', 'accepted_at']


# 과정별 수강 통계용
class CourseEnrollmentStatsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    total_enrollments = serializers.IntegerField()
    pending_enrollments = serializers.IntegerField()
    approved_enrollments = serializers.IntegerField()
    rejected_enrollments = serializers.IntegerField()
    generations = serializers.ListField(
        child=serializers.DictField(),
        help_text="과정별 기수별 등록 현황"
    )


# 과정별 수강 목록
class CourseEnrollmentListSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    enrollments = EnrollmentRequestSerializer(many=True)


# 기수 간단 조회용
class GenerationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ['id', 'number', 'status', 'start_at', 'end_at']


# 관리자용 과정 목록 조회용
class CourseAdminListSerializer(serializers.ModelSerializer):
    generations = GenerationSimpleSerializer(source='generation_set', many=True, read_only=True)
    active_generations = serializers.SerializerMethodField()
    total_student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "name", "tag", "description", "thumbnail_img_url",
            "created_at", "updated_at",
            "generations", "active_generations", "total_student_count"
        ]

    def get_active_generations(self, obj):
        active = obj.generation_set.filter(status="ONGOING")
        return GenerationSimpleSerializer(active, many=True).data

    def get_total_student_count(self, obj):
        return StudentEnrollmentRequest.objects.filter(
            generation__course=obj,
            status__in=["APPROVED", "COMPLETED"]
        ).count()


# 관리자 외 사용자 목록 조회용 (간단 버전)
class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "name", "tag", "description",
            "thumbnail_img_url", "created_at", "updated_at"
        ]
        read_only_fields = fields


# 등록/수정/상세 조회용
class CourseSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "name", "tag", "description",
            "thumbnail_img_url", "created_at", "updated_at",
            "student_count"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count"]

    def get_student_count(self, course):
        return StudentEnrollmentRequest.objects.filter(
            generation__course=course,
            status="APPROVED"
        ).count()

    # 중복 유효성 검사
    def validate_name(self, value):
        if self.instance is None or self.instance.name != value:
            if Course.objects.filter(name=value).exists():
                raise serializers.ValidationError("이미 존재하는 과정 이름입니다.")
        return value

    def validate_tag(self, value):
        if self.instance is None or self.instance.tag != value:
            if Course.objects.filter(tag=value).exists():
                raise serializers.ValidationError("이미 존재하는 과정 태그입니다.")
        return value

