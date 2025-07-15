from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.tests.core.utils.grading import (
    calculate_correct_count,
    calculate_total_score,
    validate_answers_json_format,
)
from apps.tests.models import TestSubmission
from apps.tests.serializers.test_deployment_serializers import (
    AdminTestDeploymentSerializer,
    AdminTestListDeploymentSerializer,
    UserTestDeploymentSerializer,
)
from apps.users.models import PermissionsStudent, User


# 관리자 쪽지 시험 응시 상세 조회
class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("name", "nickname")


# 관리자 쪽지 시험 응시 상세 조회
class StudentSerializer(serializers.ModelSerializer[PermissionsStudent]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PermissionsStudent
        fields = ("user",)


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListUserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("name", "nickname")


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListStudentSerializer(serializers.ModelSerializer[PermissionsStudent]):
    user = AdminListUserSerializer(read_only=True)

    class Meta:
        model = PermissionsStudent
        fields = ("user",)


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestSubmissionListSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = AdminTestListDeploymentSerializer(read_only=True)
    student = AdminListStudentSerializer(read_only=True)
    # total_score = serializers.SerializerMethodField()

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "student", "cheating_count", "score", "started_at", "created_at")


# 관리자 쪽지 시험 응시 전체 목록 조회 검색 필터
class TestSubmissionFilterSerializer(serializers.Serializer):
    subject_title = serializers.CharField(required=False, allow_blank=True)
    course_title = serializers.CharField(required=False, allow_blank=True)
    generation_number = serializers.IntegerField(required=False)
    ordering = serializers.ChoiceField(
        choices=[
            ("latest", "최신순"),
            ("total_score_desc", "점수가 높은 순"),
            ("total_score_asc", "점수가 낮은 순"),
        ],
        default="latest",
        required=False,
    )
    score = serializers.IntegerField(required=False, min_value=0)
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=10, required=False)


# 관리자 쪽지 시험 응시 상세 조회
class AdminTestDetailSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = AdminTestDeploymentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    duration_minute = serializers.SerializerMethodField()

    class Meta:
        model = TestSubmission
        fields = (
            "id",
            "deployment",
            "student",
            "cheating_count",
            "started_at",
            "answers_json",
            "score",
            "correct_count",
            "duration_minute",
        )

    # 응시 소요 시간(분)
    def get_duration_minute(self, obj):
        if not obj.started_at or not obj.created_at:
            return None
        delta = obj.created_at - obj.started_at
        if delta.total_seconds() < 0:
            raise ValidationError("시험 종료 시간이 시작 시간보다 빠릅니다.")
        return int(delta.total_seconds() // 60)


# 수강생 쪽지 시험 제출
class UserTestSubmitSerializer(serializers.ModelSerializer[TestSubmission]):
    answers_json = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))

    class Meta:
        model = TestSubmission
        fields = (
            "started_at",
            "cheating_count",
            "answers_json",
        )

    def validate_answers_json(self, value):
        snapshot = self.context["snapshot"]
        validate_answers_json_format(value, snapshot)

        return value

    def create(self, validated_data):
        snapshot = self.context["snapshot"]
        data = validated_data.copy()
        data["score"] = calculate_total_score(validated_data["answers_json"], snapshot)
        data["correct_count"] = calculate_correct_count(validated_data["answers_json"], snapshot)
        submission = TestSubmission.objects.create(**data)
        return submission


# 사용자 쪽지 시험 결과 조회
class UserTestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "cheating_count", "answers_json")
