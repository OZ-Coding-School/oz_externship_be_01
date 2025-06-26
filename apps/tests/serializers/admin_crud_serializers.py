from typing import Any, Dict

from rest_framework import serializers

from apps.courses.models import Subject
from apps.tests.models import Test, TestQuestion


# 쪽지시험 수정
class AdminTestUpdateSerializer(serializers.ModelSerializer[Test]):
    subject_id = serializers.IntegerField()

    class Meta:
        model = Test
        fields = ("id", "title", "subject_id", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            raise serializers.ValidationError("수정할 데이터가 없습니다.")
        return data


# 쪽지시험 상세조회 (Test 모델의 ForeignKey 필드로 연결된 Subject를 직렬화)
class SubjectSerializer(serializers.ModelSerializer[Test]):
    name = serializers.CharField(source="title")  # api 명세서 맞춤 / 식별용 문자 name 사용

    class Meta:
        model = Subject
        fields = ("id", "name")


# 쪽지시험 상세조회 (Test 모델과 연결된 여러 개의 TestQuestion을 직렬화)
class TestQuestionSimpleSerializer(serializers.ModelSerializer["TestQuestion"]):
    class Meta:
        model = TestQuestion
        fields = ("id", "type", "question", "point")


# 쪽지시험 상세조회 Nested Serializer
class TestDetailSerializer(serializers.ModelSerializer[Test]):
    subject = SubjectSerializer()
    questions = TestQuestionSimpleSerializer(many=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = (
            "id",
            "title",
            "subject",
            "question_count",
            "questions",
            "created_at",
            "updated_at",
        )

    def get_question_count(self, obj: Test) -> int:
        return obj.questions.count()


# 쪽지시험 목록조회 Nested 구조 사용안함 응답 단순화
class TestListSerializer(serializers.ModelSerializer[Test]):
    subject_name = serializers.CharField(source="subject.title")
    question_count = serializers.IntegerField()
    submission_count = serializers.IntegerField()

    class Meta:
        model = Test
        fields = (
            "id",
            "title",
            "subject_name",
            "question_count",
            "submission_count",
            "created_at",
            "updated_at",
        )


# 쪽지시험 생성
class TestCreateSerializer(serializers.ModelSerializer[Test]):
    subject_id = serializers.IntegerField()

    class Meta:
        model = Test
        fields = ("id", "title", "subject_id", "thumbnail_img_url", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: Dict[str, Any]) -> Test:
        subject_id: int = validated_data.pop("subject_id")
        validated_data["subject_id"] = subject_id
        return Test.objects.create(**validated_data)
