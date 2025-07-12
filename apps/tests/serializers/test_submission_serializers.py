from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.tests.core.utils.grading import (
    calculate_correct_count,
    calculate_total_score,
    get_questions_snapshot_from_submission,
    validate_answers_json_format,
)
from apps.tests.models import TestSubmission
from apps.tests.serializers.test_deployment_serializers import (
    AdminTestDeploymentSerializer,
    AdminTestListDeploymentSerializer,
    UserTestDeploymentListSerializer,
    UserTestDeploymentSerializer,
)
from apps.tests.serializers.test_serializers import UserTestSerializer
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

    # 총 점수
    # def get_total_score(self, obj):
    #     snapshot = get_questions_snapshot_from_submission(obj)
    #     validate_answers_json_format(obj.answers_json, snapshot)
    #     return calculate_total_score(obj.answers_json, snapshot)

    # 맞은 문제 수
    # def get_correct_count(self, obj):
    #     snapshot = get_questions_snapshot_from_submission(obj)
    #     validate_answers_json_format(obj.answers_json, snapshot)
    #     return calculate_correct_count(obj.answers_json, snapshot)

    # 총 문제 수
    # def get_total_questions(self, obj):
    #     snapshot = get_questions_snapshot_from_submission(obj)
    #     if not isinstance(snapshot, list):
    #         raise ValidationError("questions_snapshot_json은 리스트 형식이어야 합니다.")
    #     return len(snapshot)


# 수강생 쪽지 시험 제출
class UserTestSubmitSerializer(serializers.ModelSerializer[TestSubmission]):
    student = serializers.PrimaryKeyRelatedField(queryset=PermissionsStudent.objects.all())
    answers_json = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))

    class Meta:
        model = TestSubmission
        fields = (
            "student",
            "started_at",
            "cheating_count",
            "answers_json",
        )

    def validate(self, data):
        deployment = self.context["deployment"]
        permission_student = self.context["student"]
        user = self.context["request"].user
        now = timezone.now()

        if permission_student.user != user:
            raise serializers.ValidationError("인증된 사용자와 수강생 정보가 일치하지 않습니다.")

        if permission_student.id != data.get("student").id:
            raise serializers.ValidationError("사용자의 수강생 ID와 일치하지 않습니다.")

        if not data.get("answers_json"):
            raise serializers.ValidationError("모든 답안이 제출되지 않았습니다.")

        if deployment is None:
            raise serializers.ValidationError("시험 정보가 없습니다.")

        if deployment.close_at and deployment.close_at < now:
            raise serializers.ValidationError("시험 제출 시간이 지났습니다.")

        return data

    def create(self, validated_data):
        deployment = self.context["deployment"]
        now = timezone.now()

        # 자동 제출 조건 처리
        self.auto_submit_message = None
        cheating_count = validated_data.get("cheating_count", 0)

        if deployment.close_at and deployment.close_at < now:
            self.auto_submit_message = "시험 제출 시간이 지나 자동 제출 되었습니다."
        elif int(cheating_count) >= 3:
            self.auto_submit_message = "부정행위 3회 이상 적발되어 자동 제출 처리되었습니다."

        validated_data["deployment"] = deployment

        return super().create(validated_data)


# 사용자 쪽지 시험 목록 조회
class UserTestSubmissionListSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentListSerializer(read_only=True)

    score = serializers.SerializerMethodField()
    correct_count = serializers.SerializerMethodField()

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "score", "correct_count")

    def get_score(self, obj: TestSubmission):
        # 응시한 경우만 점수 반환
        return obj.score

    def get_correct_count(self, obj: TestSubmission):
        return obj.correct_count


# 관리자 쪽지 시험 응시 전체 목록 조회 검색 필터
class TestSubmissionListFilterSerializer(serializers.Serializer):
    course_title = serializers.CharField(required=False, allow_blank=True)
    generation_number = serializers.IntegerField(required=False)
    submission_status = serializers.ChoiceField(
        choices=[
            ("completed", "응시완료"),
            ("not_submitted", "미응시"),
        ],
        required=False,
    )


# 사용자 쪽지 시험 결과 조회
class UserTestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "cheating_count", "answers_json")
