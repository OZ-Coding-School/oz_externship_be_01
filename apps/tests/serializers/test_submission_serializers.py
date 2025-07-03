from django.utils import timezone
from rest_framework import request, serializers

from apps.tests.models import TestDeployment, TestSubmission
from apps.tests.serializers.test_deployment_serializers import (
    AdminTestDeploymentSerializer,
    AdminTestListDeploymentSerializer,
    UserTestDeploymentSerializer,
)
from apps.users.models import PermissionsStudent, User


# 공통 Admin
class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("id", "name", "nickname")


# 공통 Admin & User
class StudentSerializer(serializers.ModelSerializer[PermissionsStudent]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PermissionsStudent
        fields = ("id", "user")


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
class AdminTestListSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = AdminTestListDeploymentSerializer(read_only=True)
    student = AdminListStudentSerializer(read_only=True)
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "student", "cheating_count", "total_score", "started_at", "created_at")

    def get_total_score(self, obj):
        return 30  # 그냥 고정 점수 예시


# 관리자 쪽지 시험 응시 상세 조회
class AdminTestDetailSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = AdminTestDeploymentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = (
            "id",
            "deployment",
            "student",
            "cheating_count",
            "started_at",
            "answers_json",
        )


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
        read_only_fields = ("started_at",)

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
        validated_data["started_at"] = timezone.now()

        return super().create(validated_data)


# 사용자 쪽지 시험 결과 조회
class UserTestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "cheating_count", "answers_json")
