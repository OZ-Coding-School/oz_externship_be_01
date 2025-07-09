import json
import uuid
from typing import Any, Dict

from django.utils import timezone
from rest_framework import serializers

from apps.courses.models import Subject
from apps.tests.models import Test, TestQuestion
from core.utils.s3_file_upload import S3Uploader


# 쪽지시험 수정
class AdminTestUpdateSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(required=False)
    thumbnail_file = serializers.ImageField(write_only=True, required=False)  # 이미지 수정용 필드
    thumbnail_img_url = serializers.URLField(read_only=True)  # 수정 후 응답에 이미지 경로 제공

    class Meta:
        model = Test
        fields = ("id", "title", "subject_id", "thumbnail_file", "thumbnail_img_url", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("수정할 데이터가 없습니다.")
        return data

    def validate_subject_id(self, value):
        if not Subject.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid subject ID.")
        return value

    def update(self, instance: Test, validated_data):
        # 제목 수정
        if "title" in validated_data:
            instance.title = validated_data["title"]

        # 과목 수정
        if "subject_id" in validated_data:
            instance.subject_id = validated_data["subject_id"]

        # 썸네일 파일이 넘어온 경우, S3에 덮어쓰기 후 URL 업데이트
        if "thumbnail_file" in validated_data:
            thumbnail_file = validated_data.pop("thumbnail_file")
            uploader = S3Uploader()
            updated_url = uploader.update_file(thumbnail_file, instance.thumbnail_img_url)
            if not updated_url:
                raise serializers.APIException("S3 이미지 업로드 실패")
            instance.thumbnail_img_url = updated_url

        instance.updated_at = timezone.now()
        instance.save()
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
            "explanation",
        )

    def get_options(self, obj):
        if obj.options_json:
            try:

                return json.loads(obj.options_json)
            except Exception:
                return []
        return []


# 쪽지시험 상세조회용 시리얼라이저
class TestDetailSerializer(serializers.ModelSerializer):
    subject = TestSubjectSerializer()
    questions = TestQuestionDetailSerializer(many=True)  # nested serializer로 수정
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = (
            "id",
            "title",
            "subject",
            "thumbnail_img_url",
            "question_count",
            "questions",
            "created_at",
            "updated_at",
        )

    def get_question_count(self, obj):
        # context 사용하지 않고 obj의 전체 문제 수 반환
        return obj.questions.count()

    def get_questions(self, obj):
        # context 사용하지 않고 obj의 전체 문제 리스트 직렬화
        return TestQuestionDetailSerializer(obj.questions.all(), many=True).data


# 쪽지시험 목록조회
class TestListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.title")
    question_count = serializers.IntegerField()
    submission_count = serializers.IntegerField()
    detail_url = serializers.SerializerMethodField()

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
            "detail_url",
        )

    def get_detail_url(self, obj):
        return f"/api/v1/admin/tests/{obj.id}/"


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

    def validate_subject_id(self, value):
        from apps.courses.models import Subject

        if not Subject.objects.filter(id=value).exists():
            raise serializers.ValidationError("유효하지 않은 subject_id 입니다.")
        return value

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}

        subject_id = validated_data.pop("subject_id")
        thumbnail_file = validated_data.pop("thumbnail_file")

        subject = Subject.objects.get(id=subject_id)

        # Test 생성
        test = Test.objects.create(
            title=validated_data["title"],
            subject=subject,
            thumbnail_img_url="",  # 업로드 전 임시 저장
        )

        # S3 업로드 key에 test.id 포함 + 난수 추가
        random_str = uuid.uuid4().hex[:6]
        s3_key = f"oz_externship_be/tests/thumbnail_images/{test.id}_{random_str}.png"

        uploader = S3Uploader()
        thumbnail_img_url = uploader.upload_file(thumbnail_file, s3_key)
        if thumbnail_img_url is None:
            raise serializers.APIException("S3 업로드 실패")

        test.thumbnail_img_url = thumbnail_img_url
        test.save()
        return test


# 상인님 subject 임포트 중이었는데, id가 필요없어서 새로 생성
# 관리자 쪽지 시험 응시 전체 목록 조회, 상세 조회, 사용자 응시
class CommonSubjectSerializer(serializers.ModelSerializer[Subject]):

    class Meta:
        model = Subject
        fields = ("title",)


# 관리자 쪽지 시험 응시 상세 조회
class AdminTestDetailSerializer(serializers.ModelSerializer[Test]):
    subject = CommonSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("subject", "title", "created_at", "updated_at")


# 사용자 쪽지 시험 응시
class UserTestSerializer(serializers.ModelSerializer[Test]):
    subject = CommonSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("subject", "title", "thumbnail_img_url")


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestListSerializer(serializers.ModelSerializer[Test]):
    subject = CommonSubjectSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ("subject", "title")
