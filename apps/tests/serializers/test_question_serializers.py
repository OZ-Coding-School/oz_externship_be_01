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
    prompt = serializers.CharField(required=False, allow_blank=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
    answer = serializers.JSONField()

    def validate_answer(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("OX 문제의 답변은 문자열이어야 합니다.")
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
class TestQuestionUpdateSerializer(serializers.ModelSerializer):  # type: ignore
    prompt = serializers.CharField(required=False, allow_blank=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
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

    # 요청값 기준으로만 판단
    def validate(self, data):
        question_type = data.get("type", None)
        answer = data.get("answer", None)
        point = data.get("point", None)
        options = data.get("options_json", None)
        prompt = data.get("prompt", None)
        blank_count = data.get("blank_count", None)

        if not question_type:
            raise serializers.ValidationError({"detail": "문제 유형(type)은 필수입니다."})

        if point is not None and not (1 <= point <= 10):
            raise serializers.ValidationError({"detail": "배점은 1~10점 사이여야 합니다."})

        # 유형별 필드 검증 및 불필요한 필드 초기화
        if question_type == "multiple choice":
            if not options:
                raise serializers.ValidationError({"detail": "다지선다형은 'option_json'이 필수입니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다."})

            data["prompt"] = None
            data["options_json"] = None

        elif question_type == "blank_count":
            if not prompt:
                raise serializers.ValidationError({"detail": "빈칸 문제는 'prompt'가 필요합니다."})
            if blank_count is None or blank_count < 1:
                raise serializers.ValidationError({"detail": "blank_count는 1이상이어야 합니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다."})

            data["options_json"] = None

        elif question_type == "subjective":
            if not answer:
                raise serializers.ValidationError({"detail": "주관식 문제는 정답이 필요합니다."})

            data["prompt"] = None
            data["options_json"] = None
            data["blank_count"] = None

        elif question_type == "order":
            if not options or len(options) < 2:
                raise serializers.ValidationError({"detail": "순서 문제는 보기(options_json) 2개 이상 필요합니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다.."})

            data["prompt"] = None
            data["blank_count"] = None

        elif question_type == "ox":
            if answer not in [["o"], ["x"]]:
                raise serializers.ValidationError({"detail": "ox 문제는 정답이 ['o'] 또는 ['x']여야 합니다."})

            data["prompt"] = None
            data["blank_count"] = None
            data["options_json"] = None

        else:
            raise serializers.ValidationError({"detail": f"지원하지 않는 문제 유형입니다: {question_type}"})

        return data


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
    prompt = serializers.CharField(write_only=True)
    blank_count = serializers.IntegerField(write_only=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
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
            return TestQuestion.objects.bulk_create(question_models)
