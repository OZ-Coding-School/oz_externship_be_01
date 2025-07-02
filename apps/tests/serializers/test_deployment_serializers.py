from typing import Any, Dict

from rest_framework import serializers

from apps.courses.models import Course, Generation
from apps.tests.models import Test, TestDeployment
from apps.tests.models import TestDeployment, TestQuestion
from apps.tests.serializers.test_question_serializers import (
    UserTestQuestionStartSerializer,
)
from apps.tests.serializers.test_serializers import (
    AdminTestSerializer,
    CommonTestSerializer,
)


# 공통 User&Admin
class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("id", "name")


# 공통 User&Admin
class GenerationSerializer(serializers.ModelSerializer[Generation]):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("id", "course", "number")


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListCourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("name",)


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminListGenerationSerializer(serializers.ModelSerializer[Generation]):
    course = AdminListCourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("course", "number")


# 공통 AdminTestDeploymentSerializer
class AdminTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestSerializer(read_only=True)
    generation = GenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
            "questions_snapshot_json",
        )


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestListDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = CommonTestSerializer(read_only=True)
    generation = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation",
        )


# 사용자 쪽지 시험 응시: 요청, access_code 검증용
class UserTestStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestDeployment
        fields = ("access_code",)
        # extra_kwargs = {
        #     "access_code": {"write_only": True},
        # }
        extra_kwargs = {
            "access_code": {
                "write_only": True,
                "required": True,
                "error_messages": {"required": "시험 코드를 입력해 주세요."},
            }
        }

        # access_code 유효성 검사

    def validate_access_code(self, value: str) -> str:
        """
        access_code 유효 여부 확인
        """
        if not TestDeployment.objects.filter(access_code=value).exists():
            raise serializers.ValidationError("등록되지 않은 시험 코드입니다.")
        return value


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = CommonTestSerializer(read_only=True)
    questions_snapshot_json = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "duration_time",
            "questions_snapshot_json",
        )

    def get_questions_snapshot_json(self, obj):
        question_ids = [q["id"] for q in obj.questions_snapshot_json]
        questions = TestQuestion.objects.filter(id__in=question_ids)

        # 질문 ID 순서 보존 (questions는 쿼리셋이라 순서가 안 맞을 수 있음)
        id_to_question = {q.id: q for q in questions}
        ordered_questions = [id_to_question[qid] for qid in question_ids if qid in id_to_question]

        return UserTestQuestionStartSerializer(ordered_questions, many=True).data




# 🔹 공통 timestamp serializer (선택적)
class BaseTimestampedSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        abstract = True
        fields = ["created_at", "updated_at"]


# 🔹 Test (쪽지시험)
class TestSerializer(BaseTimestampedSerializer):
    subject: Any = serializers.StringRelatedField()  # Subject 모델의 __str__() 출력


class Meta(BaseTimestampedSerializer.Meta):
    model = Test
    fields = ["id", "subject", "title", "thumbnail_img_url", *BaseTimestampedSerializer.Meta.fields]


# 활성화 ,비황성화
class DeploymentStatusUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = TestDeployment
        fields = ["status"]
        extra_kwargs = {"status": {"required": True}}


# 🔹 TestDeployment 생성
class DeploymentCreateSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(write_only=True, help_text="시험 ID")
    generation = serializers.IntegerField(help_text="기수 ID")

    class Meta:
        model = TestDeployment
        fields = [
            "test_id",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
        ]

    def create(self, validated_data: Dict[str, Any]) -> TestDeployment:
        # DB 조회나 MOCK 처리 없이, 단순히 create 호출
        return super().create(validated_data)


# 목록 조히 시리얼 라이저 ( 모델 기반으로 할려면 DB 필요)
class DeploymentListSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField(source="id")
    test_title = serializers.CharField(source="test.title")
    subject_title = serializers.CharField(source="test.subject.title")
    course_generation = serializers.SerializerMethodField()
    total_participants = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_course_generation(self, obj: Dict[str, Any]) -> str:
        course: str = obj.get("generation", {}).get("course", {}).get("title", "")
        generation: str = obj.get("generation", {}).get("name", "")
        return f"{course} {generation}"

    def get_total_participants(self, obj: Dict[str, Any]) -> int:
        return int(obj.get("total_participants", 0))

    def get_average_score(self, obj: Dict[str, Any]) -> float:
        return int(obj.get("average_score", 0.0))


class DeploymentDetailSerializer(serializers.Serializer[Any]):
    # 🔹 시험 정보
    test_id = serializers.IntegerField(source="test.id")
    test_title = serializers.CharField(source="test.title")
    subject_title = serializers.CharField(source="test.subject.title")
    question_count = serializers.SerializerMethodField()

    # 🔹 배포 정보
    deployment_id = serializers.IntegerField(source="id")
    access_code = serializers.CharField()
    access_url = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="generation.course.title")
    generation_name = serializers.CharField(source="generation.name")
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    # 🔹 응시 정보
    total_participants = serializers.IntegerField()
    unsubmitted_participants = serializers.IntegerField()

    # ⬇️ Custom 필드 처리
    def get_access_url(self, obj: Any) -> str:
        return f"https://ozschool.com/test/{obj['id']}?code={obj['access_code']}"

    def get_question_count(self, obj: Any) -> int:
        snapshot = obj.get("questions_snapshot_json", {})
        return len(snapshot)


# # 🔹 참가코드 구현 (유효성 검사라서 모델을 계승하지 않음) (잘목 만듬)
# class AdminCodeValidationSerializer(serializers.Serializer[Any]):
#     deployment_id = serializers.IntegerField(help_text="배포 ID")
#     access_code = serializers.CharField(max_length=64, help_text="참가 코드")


# 참가 코드 검증 (user)
class UserCodeValidationSerializer(serializers.Serializer):
    access_code = serializers.CharField(write_only=True)

    def validate_access_code(self, value: str) -> str:
        test_deployment = self.context["test_deployment"]
        if test_deployment.access_code != value:
            raise serializers.ValidationError("유효하지 않은 참가코드입니다.")
        return value


class TestDeploymentStatusValidateSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["Activated", "Deactivated"])
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
