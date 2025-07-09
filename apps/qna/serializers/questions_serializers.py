import time
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.qna.serializers.answers_serializers import AnswerListSerializer
from core.utils.s3_file_upload import S3Uploader


# 질문 이미지
class QuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


# 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer):
    image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False, allow_empty=True, max_length=5
    )
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = ["title", "content", "category_id", "image_files"]

    def validate_category_id(self, value: int) -> QuestionCategory:
        try:
            category = QuestionCategory.objects.get(id=value)
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 카테고리입니다.")

        if category.category_type != "minor":
            raise serializers.ValidationError("소분류 카테고리만 선택할 수 있습니다.")

        return category

    def validate_image_files(self, value: list[UploadedFile]) -> list[UploadedFile]:
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
        return value

    def create(self, validated_data: dict[str, Any]) -> Question:
        # TODO : 개발 단계: AnonymousUser 처리 이후 삭제 필요
        from django.contrib.auth.models import AnonymousUser

        from apps.users.models import User

        image_files: list[UploadedFile] = validated_data.pop("image_files", [])
        category: QuestionCategory = validated_data.pop("category_id")
        author = validated_data.pop("author")
        # TODO : 개발 단계: AnonymousUser일 경우 더미 사용자로 대체/ 개발 이후 삭제 필요
        if isinstance(author, AnonymousUser):
            author, _ = User.objects.get_or_create(
                email="testuser@example.com", defaults={"nickname": "test", "profile_image_url": "", "is_active": True}
            )

        with transaction.atomic():
            question = Question.objects.create(category=category, author=author, **validated_data)

            uploader = S3Uploader()
            for index, img in enumerate(image_files, 1):
                # 직관적이고 유일한 파일명: question_질문ID_image_순번_타임스탬프.확장자
                img_name = getattr(img, "name", None)
                if isinstance(img_name, str) and "." in img_name:
                    file_extension = img_name.split(".")[-1]
                else:
                    file_extension = "jpg"
                timestamp = int(time.time() * 1000)
                filename = f"question_{question.id}_image_{index}_{timestamp}.{file_extension}"
                s3_key = f"qna/questions/{filename}"
                url = uploader.upload_file(img, s3_key)
                if not url:
                    raise serializers.ValidationError("이미지 업로드에 실패했습니다.")
                QuestionImage.objects.create(question=question, img_url=url)

        return question


# 질문 수정
class QuestionUpdateSerializer(serializers.ModelSerializer[Question]):
    images = QuestionImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    category_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Question
        fields = ["category", "category_id", "title", "content", "images", "image_files"]
        read_only_fields = ["category"]
        extra_kwargs = {
            "title": {"required": False},
            "content": {"required": False},
            "category_id": {"required": False},
        }


# 카테고리 이름
class CategoryNameSerializer(serializers.ModelSerializer):
    major = serializers.SerializerMethodField()
    middle = serializers.SerializerMethodField()
    minor = serializers.CharField(source="name")

    class Meta:
        model = QuestionCategory
        fields = ["major", "middle", "minor"]

    def get_major(self, obj):
        if obj.parent and obj.parent.parent:
            return obj.parent.parent.name
        return None

    def get_middle(self, obj):
        if obj.parent:
            return obj.parent.name
        return None


# 작성자 정보
class AuthorInfoSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    profile_image_url = serializers.CharField()


# 질문 목록 조회
class QuestionListSerializer(serializers.ModelSerializer):
    category = CategoryNameSerializer(read_only=True)
    author = AuthorInfoSerializer(read_only=True)
    answer_count = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "author",
            "category",
            "answer_count",
            "view_count",
            "created_at",
            "thumbnail",
        ]

    def get_answer_count(self, obj):
        return obj.answers.count()

    def get_thumbnail(self, obj):
        img = obj.images.first()
        if img:
            return img.img_url
        return None


# 질문 상세 조회
class QuestionDetailSerializer(serializers.ModelSerializer[Question]):
    images = QuestionImageSerializer(many=True, read_only=True)
    author = AuthorInfoSerializer(read_only=True)
    category = CategoryNameSerializer(read_only=True)
    answers = AnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "images", "author", "category", "view_count", "created_at", "answers"]
