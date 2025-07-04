from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.courses.models import Subject
from apps.tests.models import Test, TestQuestion


# 쪽지시험 수정
class AdminTestUpdateSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(required=False)
    thumbnail_file = serializers.ImageField(write_only=True, required=False)  # 이미지 수정용 필드
    thumbnail_img_url = serializers.URLField(read_only=True)  # 수정 후 응답에 이미지 경로 제공

    class Meta:
        model = Test
        fields = ("id", "title", "subject_id", "thumbnail_file", "thumbnail_img_url", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            raise serializers.ValidationError("수정할 데이터가 없습니다.")
        return data

    def update(self, instance: Test, validated_data: dict[str, Any]) -> Test:
        # 제목 수정
        if "title" in validated_data:
            instance.title = validated_data["title"]

        # 과목 수정
        if "subject_id" in validated_data:
            instance.subject_id = validated_data["subject_id"]

        # 로고 이미지 수정
        if "thumbnail_file" in validated_data:
            thumbnail_file = validated_data.pop("thumbnail_file")
            # 실제 서비스에서는 이미지 업로드 후 URL 생성 필요

            instance.thumbnail_img_url = f"https://my-cdn.com/{thumbnail_file.name}"

        instance.updated_at = timezone.now()
        # instance.save() 추후  DB 반영
        return instance


# 쪽지시험 상세조회 (Test 모델의 ForeignKey 필드로 연결된 Subject를 직렬화)
class TestSubjectSerializer(serializers.ModelSerializer[Test]):
    name = serializers.CharField(source="title")  # api 명세서 맞춤 / 식별용 문자 name 사용

    class Meta:
        model = Subject
        fields = ("id", "name")


# 쪽지시험 상세조회 (Test 모델과 연결된 여러 개의 TestQuestion을 직렬화)
class TestQuestionSimpleSerializer(serializers.ModelSerializer["TestQuestion"]):
    class Meta:
        model = TestQuestion
        fields = ("id", "type", "question", "point")


# 쪽지시험 문제 단일 직렬화용
class TestQuestionDetailSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = TestQuestion
        fields = (
            "id",
            "type",
            "question",
            "point",
            "prompt",
            "options",
            "answer",
        )

    def get_options(self, obj):
        if obj.options_json:
            try:
                import json

                return json.loads(obj.options_json)
            except Exception:
                return []
        return []


# 쪽지시험 상세조회용 시리얼라이저
class TestDetailSerializer(serializers.ModelSerializer):
    subject = TestSubjectSerializer()
    questions = serializers.SerializerMethodField()  # context 기반 직렬화로 수정
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

    def get_question_count(self, obj):
        questions = self.context.get("questions")
        if questions is not None:
            return len(questions)
        return obj.questions.count()

    def get_questions(self, obj):
        questions = self.context.get("questions")
        if questions is not None:
            return TestQuestionDetailSerializer(questions, many=True).data
        return TestQuestionDetailSerializer(obj.questions.all(), many=True).data


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
    thumbnail_file = serializers.ImageField(write_only=True, required=True)
    thumbnail_img_url = serializers.URLField(read_only=True)

    class Meta:
        model = Test
        fields = (
            "id",
            "title",
            "subject_id",
            "thumbnail_file",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: Dict[str, Any]) -> Test:
        subject_id: int = validated_data.pop("subject_id")
        validated_data["subject_id"] = subject_id
        return Test.objects.create(**validated_data)


# 공통 AdminTestSerializer
class AdminTestSerializer(serializers.ModelSerializer[Test]):
    subject = TestSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("id", "subject", "title", "created_at", "updated_at")


# 공통 UserTestSerializer
class UserTestSerializer(serializers.ModelSerializer[Test]):
    subject = TestSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("id", "subject", "title", "thumbnail_img_url")


# 관리자 쪽지 시험 응시 전체 목록 조회, 사용자 응시
class CommonSubjectSerializer(serializers.ModelSerializer[Subject]):

    class Meta:
        model = Subject
        fields = ("title",)


# 관리자 쪽지 시험 응시 전체 목록 조회, 사용자 응시
class CommonTestSerializer(serializers.ModelSerializer[Test]):
    subject = CommonSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("subject", "title")
