from typing import Any

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.relations import PrimaryKeyRelatedField

from apps.tests.core.utils.question_validator import QuestionValidator
from apps.tests.models import Test, TestQuestion


# 등록
class TestQuestionCreateSerializer(serializers.ModelSerializer, QuestionValidator):  # type: ignore
    test_id = serializers.IntegerField(write_only=True)
    test: PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(read_only=True)
    prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    answer = serializers.ListField(child=serializers.CharField())

    def validate_answer(self, value):
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise serializers.ValidationError("정답은 문자열 리스트 형식이어야 합니다.")
        return value

    class Meta:
        model = TestQuestion
        fields = "__all__"

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        test_id = data.get("test_id")
        if not test_id:
            raise serializers.ValidationError("test_id는 필수입니다.")
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise NotFound(f"해당 ID({test_id})의 쪽지시험이 존재하지 않습니다.")

        # 문제 개수 제한 (최대 20개)
        self.validatequestions_length_at_db(test)
        self.validate_point_field(test=test, point=data["point"])

        validated_data = self.validate_question_by_type(data=data)
        return validated_data

    def create(self, validated_data):
        test_id = validated_data.pop("test_id")
        test = Test.objects.get(id=test_id)
        return TestQuestion.objects.create(test=test, **validated_data)


# 수정
class TestQuestionUpdateSerializer(serializers.ModelSerializer, QuestionValidator):  # type: ignore
    prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    answer = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TestQuestion
        fields = [
            "type",
            "question",
            "prompt",
            "blank_count",
            "options_json",
            "answer",
            "point",
            "explanation",
        ]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        question_type = data.get("type")
        if not question_type:
            raise serializers.ValidationError({"detail": "문제 유형(type)은 필수입니다."})

        if "point" in data and not (1 <= data["point"] <= 10):
            raise serializers.ValidationError({"detail": "배점은 1~10점 사이여야 합니다."})

        # 핵심 변경: 유형별 검증 위임
        return self.validate_question_by_type(data)


# 목록 조회
class TestListItemSerializer(serializers.ModelSerializer):  # type: ignore
    test_id = serializers.IntegerField(source="id")
    test_title = serializers.CharField(source="title")
    subject_title = serializers.CharField(source="subject.title")
    question_count = serializers.IntegerField()
    total_score = serializers.IntegerField()

    submission_status = serializers.ChoiceField(choices=["submitted", "not_submitted"])
    score = serializers.IntegerField(required=False, allow_null=True)
    correct_count = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Test
        fields = [
            "test_id",
            "test_title",
            "thumbnail_img_url",
            "subject_title",
            "question_count",
            "total_score",
            "submission_status",
            "score",
            "correct_count",
        ]


# 삭제 응답
class ErrorResponseSerializer(serializers.Serializer):  # type: ignore
    detail = serializers.CharField()


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestQuestionStartSerializer(serializers.ModelSerializer[TestQuestion]):
    class Meta:
        model = TestQuestion
        fields = ("type", "question", "prompt", "blank_count", "options_json", "point")


class TestQuestionCreateBaseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=TestQuestion.QuestionType.choices, write_only=True)
    question = serializers.CharField(write_only=True)
    prompt = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    blank_count = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    options_json = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    answer = serializers.ListField(child=serializers.CharField(), write_only=True)
    point = serializers.IntegerField(write_only=True)
    explanation = serializers.CharField(write_only=True)


class TestQuestionBulkCreateSerializer(serializers.Serializer, QuestionValidator):
    test_id = serializers.IntegerField(write_only=True)
    questions = serializers.ListField(child=TestQuestionCreateBaseSerializer(), write_only=True)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        test_id = data.get("test_id")
        if not test_id:
            raise serializers.ValidationError("test_id는 필수입니다.")
        try:
            test = Test.objects.prefetch_related("questions").get(id=test_id)
        except Test.DoesNotExist:
            raise NotFound(f"해당 ID({test_id})의 쪽지시험이 존재하지 않습니다.")

        validated_data = []
        total_request_question_score = 0
        # 문제 개수 제한 (최대 20개)
        self.validate_questions_length(data=data["questions"])
        # validate total point
        self.validate_questions_total_score(data=data["questions"])
        for question in data["questions"]:
            validated_data.append(self.validate_question_by_type(data=question))

        return {"test": test, "questions": validated_data}

    def create(self, validated_data: dict[str, Any]) -> list[TestQuestion]:
        test = validated_data.pop("test")
        with transaction.atomic():
            test.questions.all().delete()
            questions = validated_data.pop("questions")
            question_models = [TestQuestion(test=test, **question) for question in questions]
            created = TestQuestion.objects.bulk_create(question_models)
            return created


class TestQuestionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestion
        fields = ["id", "question", "type", "point"]


class TestQuestionCreateResponseSerializer(serializers.ModelSerializer):
    """
    [생성 응답 전용 시리얼라이저]

    - 쪽지시험 문제 생성 후 클라이언트에게 반환할 응답 형식을 정의함
    - 모델에는 options_json이 문자열(str)로 저장되어 있지만,
      클라이언트에는 list 형식으로 반환되도록 가공함
    - answer 역시 문제 유형에 따라 list or string으로 가공해 반환함
    - 상세조회용 시리얼라이저와는 별도로, 생성 직후 응답 전용 출력 구조를 담당함
    """

    answer = serializers.SerializerMethodField()

    class Meta:
        model = TestQuestion
        fields = (
            "id",
            "test",
            "type",
            "question",
            "point",
            "prompt",
            "blank_count",
            "options_json",
            "answer",
            "explanation",
            "created_at",
            "updated_at",
        )

    def get_answer(self, obj):
        if obj.type in {
            TestQuestion.QuestionType.MULTIPLE_CHOICE_MULTI,
            TestQuestion.QuestionType.ORDERING,
            TestQuestion.QuestionType.FILL_IN_BLANK,
        }:
            return obj.answer if isinstance(obj.answer, list) else [obj.answer]
        return obj.answer
