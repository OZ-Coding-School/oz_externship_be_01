import json
from typing import Any, Dict, List

from rest_framework import serializers

# 명시적으로 임포트하여 사용합니다.
from rest_framework.exceptions import ValidationError

from apps.courses.models import Course, Generation
from apps.tests.core.utils.grading import calculate_total_score
from apps.tests.models import Test, TestDeployment, TestQuestion
from apps.tests.serializers.test_question_serializers import (
    UserTestQuestionStartSerializer,
)
from apps.tests.serializers.test_serializers import (
    AdminTestDetailSerializer,
    AdminTestListSerializer,
    UserTestSerializer,
)
from core.utils.base62 import generate_base62_code


# 공통 User&Admin
class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("id", "name")


# 삭제 공유
# 공통 User&Admin
# class GenerationSerializer(serializers.ModelSerializer[Generation]):
#     course = CourseSerializer(read_only=True)
#
#     class Meta:
#         model = Generation
#         fields = ("id", "course", "number")


# 관리자 쪽지 시험 응시 전체 목록 조회, 상세 조회
class AdminListCourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("name",)


# 관리자 쪽지 시험 응시 전체 목록 조회, 상세 조회
class AdminListGenerationSerializer(serializers.ModelSerializer[Generation]):
    course = AdminListCourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("course", "number")


# 관리자 쪽지 시험 응시 상세 조회
class AdminTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestDetailSerializer(read_only=True)
    generation = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
            "questions_snapshot_json",
        )


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestListDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestListSerializer(read_only=True)
    generation = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation",
        )


# 사용자 쪽지 시험 응시: 요청, access_code 검증용
class UserTestStartSerializer(serializers.Serializer):
    access_code = serializers.CharField(write_only=True)

    # access_code 유효성 검사
    def validate_access_code(self, value: str) -> str:
        test_deployment = self.context["test_deployment"]

        if test_deployment.access_code != value:
            raise serializers.ValidationError("유효하지 않은 참가 코드입니다.")

        return value


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = UserTestSerializer(read_only=True)
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


# 스냅샷 저장 로직( 배포 생성에 필요함)
def _generate_questions_snapshot_data(test_instance: Test) -> List[Dict[str, Any]]:
    if hasattr(test_instance, "questions") and test_instance.questions.exists():
        questions_data = [
            {
                "id": q.id,
                "question": q.question,
                "prompt": q.prompt,
                "type": q.type,
                "options_json": q.options_json,
                "answer": q.answer,
            }
            for q in test_instance.questions.all()
        ]
        return questions_data
    return []


# 활성화 ,비황성화
class DeploymentStatusUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = TestDeployment
        fields = ["status"]
        extra_kwargs = {"status": {"required": True}}


# 쪽지시험 배포 목록 조회
class DeploymentListSerializer(serializers.ModelSerializer[Any]):
    deployment_id = serializers.IntegerField(source="id", read_only=True)
    test_title = serializers.CharField(source="test.title", read_only=True)  #
    subject_title = serializers.CharField(source="test.subject.title", read_only=True)  #
    course_generation = serializers.SerializerMethodField()
    total_participants = serializers.IntegerField(read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment  #
        fields = [
            "deployment_id",  #
            "test_title",
            "subject_title",
            "course_generation",
            "total_participants",
            "average_score",
            "status",  #
            "created_at",  #
        ]

    def get_course_generation(self, obj: Any) -> str:
        course_name = obj.generation.course.name if obj.generation and obj.generation.course else ""
        generation_number = obj.generation.number if obj.generation else ""
        return f"{course_name} {generation_number}기"

    def get_average_score(self, obj: TestDeployment) -> float:
        """
        각 배포의 제출된 시험들의 평균 점수를 계산합니다.
        """
        submissions = obj.submissions.all()  # 해당 배포의 모든 제출을 가져옵니다.

        if not submissions:
            return 0.0  # 제출이 없으면 평균 점수는 0입니다.

        total_scores_sum = 0.0

        # 각 제출을 반복하며 점수를 계산하고 합산합니다.
        for submission in submissions:
            submission_score = calculate_total_score(submission.answers_json)
            total_scores_sum += submission_score

        # 전체 제출의 총합 점수를 제출 수로 나누어 평균을 계산합니다.
        return total_scores_sum / len(submissions)


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


#  쪽지시험 배포 생성
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
            raise ValidationError({"generation_id": "유효하지 않은 기수 ID 입니다."})

        # Base62 인코딩 함수를 호출하며 6자리 길이 지정을 요청
        generated_code = generate_base62_code()

        validated_data["access_code"] = generated_code
        validated_data["status"] = "Activated"

        # _generate_questions_snapshot_data 함수를 호출하여 questions_snapshot_json 필드 채우기
        questions_snapshot_data = _generate_questions_snapshot_data(test)
        validated_data["questions_snapshot_json"] = questions_snapshot_data

        return TestDeployment.objects.create(
            test=test,
            generation=generation_obj,
            **validated_data,
        )


# 참가 코드 검증 (user)
class UserCodeValidationSerializer(serializers.Serializer):
    access_code = serializers.CharField(write_only=True)

    def validate_access_code(self, value: str) -> str:
        test_deployment = self.context["test_deployment"]
        if test_deployment.access_code != value:
            raise serializers.ValidationError("유효하지 않은 참가코드입니다.")
        return value
