# access_code를 생성할 때, 무작위로 문자를 선택하여 코드를 생성ㄷ
import json
import random

# access_code를 만들 때 사용할 수 있는 기본 문자 집합을 제공
import string

# open_at, close_at 필드 처리를 위해 필요
from datetime import datetime
from typing import Any, Dict

from rest_framework import serializers

# 명시적으로 임포트하여 사용합니다.
from rest_framework.exceptions import ValidationError

from apps.courses.models import Course, Generation
from apps.tests.models import Test, TestDeployment, TestQuestion
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
        extra_kwargs = {
            "access_code": {
                "write_only": True,
                "required": True,
                "error_messages": {"required": "시험 코드를 입력해 주세요."},
            }
        }

    # access_code 유효성 검사
    def validate_access_code(self, value: str) -> str:
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
    generation_id = serializers.IntegerField(write_only=True, help_text="기수 ID")

    class Meta:
        model = TestDeployment
        fields = [
            "test_id",
            "generation_id",
            "duration_time",
            "open_at",
            "close_at",
            "questions_snapshot_json",
            "access_code",
            "status",
        ]
        read_only_fields = ["access_code", "status", "questions_snapshot_json"]

    def create(self, validated_data):
        test_id = validated_data.pop("test_id")
        generation_id = validated_data.pop("generation_id")

        # 시험 ID로 Test 모델 객체를 조회하고 없으면 유효하지 않은 시험 ID라고 에러메시지 발생
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise ValidationError({"test_id": "유효하지 않은 시험 ID 입니다."})

        # 기수 ID Generation 모델 객체를 조회하고, 없으면 유효하지 않은 기수 ID 입니다 에러메시지 발생
        try:
            # 변수명 충돌을 피하기 위해 'generation.obj로 변경
            generation_obj = Generation.objects.get(id=generation_id)
        except Generation.DoesNotExist:
            raise ValidationError({"generation": "유효하지 않은 기수 ID 입니다."})

        # 'questions'관계가 있고 데이터가 있는 경우에만 처리
        if hasattr(test, "questions") and test.questions.exists():
            validated_data["questions_snapshot_json"] = json.dumps(
                [
                    {
                        "id": q.id,
                        "question": q.question,
                        "prompt": q.prompt,
                        "type": q.type,
                        "options": getattr(q, "options_json", None),
                        "answer": q.answer,
                        "point": q.point,
                        "explanation": q.explanation,
                    }
                    for q in test.questions.all()
                ]
            )
        # 고유한 참가 코드(access_code)를 생성하여 validated_data에 추가
        validated_data["access_code"] = self._generate_unique_code()

        # 배포의 초기 상태를 'Activated'로 설정하여 validated_data에 추가
        validated_data["status"] = "Activated"
        # 모든 준비된 데이터를 사용하여 TestDeployment 모델 인스턴스를 생성하고 반환
        return TestDeployment.objects.create(
            test=test,  # Test 객체 연결
            generation=generation_obj,  # Generation 객체 연결
            **validated_data,  # 나머지 필드 (duration_time, open_at, close_at, questions, access_code, status)
        )

    # 고유한 참가코드 생성 메서드
    def _generate_unique_code(self, length=6):
        # 주어진 길이의 고유한 영숫자 코드를 생성, 데이터베이스에서 중복을 확인
        chars = string.ascii_letters + string.digits
        while True:
            code = "".join(random.choices(chars, k=length))
            if not TestDeployment.objects.filter(access_code=code).exists():
                return code


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
