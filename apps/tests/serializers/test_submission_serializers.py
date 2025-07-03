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
    # student_id = StudentSerializer(write_only=True)
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

    # 유효성 검사
    def validate(self, data):
        deployment = self.context.get("deployment")
        now = timezone.now()

        # 답안 제출 확인
        if not data.get("answers_json"):
            raise serializers.ValidationError("모든 답안이 제출되지 않았습니다.")

        # 시험 제출시간 확인
        if deployment is None:
            raise serializers.ValidationError("시험 정보가 없습니다.")

        if deployment.close_at and deployment.close_at < now:
            raise serializers.ValidationError("시험 제출 시간이 지났습니다.")

        # 중복 제출(질문하기)

        return data

    def create(self, validated_data):
        deployment = self.context["deployment"]
        student_id = validated_data.pop("student_id")

        try:
            permission_student = PermissionsStudent.objects.get(id=student_id)
        except PermissionsStudent.DoesNotExist:
            raise serializers.ValidationError("수강생 정보가 없습니다.")

        validated_data["deployment"] = deployment
        validated_data["student"] = permission_student

        return super().create(validated_data)

    # def create(self, validated_data):
    #     deployment = self.context['deployment'] or validated_data.get('deployment')
    #     user = self.context['request'].user
    #
    #     if not user.is_authenticated:
    #         raise serializers.ValidationError("인증된 사용자만 접근 가능합니다.")
    #
    #     try:
    #         permission_student = PermissionsStudent.objects.get(user=student_id)
    #     except PermissionsStudent.DoesNotExist:
    #         raise serializers.ValidationError("수강생 정보가 없습니다.")
    #
    #     if permission_student.id != validated_data.get('student_id'):
    #         raise serializers.ValidationError("사용자의 수강생 ID와 일치하지 않습니다.")
    #
    #     validated_data['deployment'] = deployment
    #     validated_data['student'] = permission_student
    #
    #     return super().create(validated_data)


# 사용자 쪽지 시험 결과 조회
class UserTestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "cheating_count", "answers_json")
