from django.utils import timezone
from rest_framework import request, serializers

from apps.tests.models import TestDeployment, TestQuestion, TestSubmission
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
class AdminTestSubmissionListSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = AdminTestListDeploymentSerializer(read_only=True)
    student = AdminListStudentSerializer(read_only=True)
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "student", "cheating_count", "total_score", "started_at", "created_at")

    @staticmethod
    def is_correct(submitted_answer, correct_answer):
        # 정답과 제출 답안이 같으면 True 반환
        return submitted_answer == correct_answer

    def get_total_score(self, obj):
        total = 0
        answers = obj.answers_json

        questions_ids = []

        # 모든 문제 ID 추출
        for qid in answers.keys():
            try:
                questions_ids.append(int(qid))
            except ValueError:
                continue

        # 한 번에 문제들 조회
        snapshot = obj.deployment.questions_snapshot_json
        question_dice = {int(q["id"]): q for q in snapshot}

        # 채점
        for question_id_str, submitted_answer in answers.items():
            try:
                question_id = int(question_id_str)
            except ValueError:
                continue

            question = question_dice.get(question_id)
            if not question:
                continue  # 문제 없으면 패스

            # snapshot의 정답과 비교
            if self.is_correct(submitted_answer, question["answer"]):
                total += question["point"]

        return total


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
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=10, required=False)


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


# 사용자 쪽지 시험 결과 조회
class UserTestResultSerializer(serializers.ModelSerializer[TestSubmission]):
    deployment = UserTestDeploymentSerializer(read_only=True)

    class Meta:
        model = TestSubmission
        fields = ("id", "deployment", "cheating_count", "answers_json")
