import time
from pathlib import Path
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import APIException

from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.users.models import User
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
                ext = Path(getattr(img, "name", "image.jpg")).suffix or ".jpg"
                timestamp = int(time.time() * 1000)
                filename = f"question_{question.id}_image_{index}_{timestamp}{ext}"
                s3_key = f"qna/questions/{filename}"
                url = uploader.upload_file(img, s3_key)
                if not url:
                    raise serializers.ValidationError("이미지 업로드에 실패했습니다.")
                QuestionImage.objects.create(question=question, img_url=url)

        return question


# 질문 수정
class QuestionUpdateSerializer(serializers.ModelSerializer):
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

    def validate_category_id(self, value):
        try:
            category = QuestionCategory.objects.get(pk=value)
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("해당 카테고리가 존재하지 않습니다.")
        if category.category_type != "minor":
            raise serializers.ValidationError("카테고리 변경은 소분류만 가능합니다.")
        return category  # validated_data에 실제 객체로 들어감

    def update(self, instance, validated_data):
        # 필드별 부분 수정
        for field in ["title", "content"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        if "category_id" in validated_data:
            instance.category = validated_data["category_id"]

        if "image_files" in validated_data:
            image_files = validated_data["image_files"]
            old_images = instance.images.all()
            old_s3_urls = [img.img_url for img in old_images]
            s3_uploader = S3Uploader()

            # 기존 이미지 DB만 삭제, S3는 보류
            old_images.delete()
            upload_success = True
            new_s3_urls = []

            for index, image_file in enumerate(image_files, 1):
                file_extension = Path(getattr(image_file, "name", "image.jpg")).suffix or ".jpg"
                timestamp = int(time.time() * 1000)
                filename = f"question_{instance.id}_image_{index}_{timestamp}{file_extension}"
                s3_key = f"qna/questions/{filename}"
                s3_url = s3_uploader.upload_file(image_file, s3_key)
                if s3_url:
                    QuestionImage.objects.create(question=instance, img_url=s3_url)
                    new_s3_urls.append(s3_url)
                else:
                    upload_success = False
                    break

            if upload_success:
                # 새 이미지 업로드 성공 시에만 S3의 옛 이미지 삭제
                for old_url in old_s3_urls:
                    s3_uploader.delete_file(old_url)
            else:
                # 업로드 중단 시, 복구 로직 (예시)
                for old_url in old_s3_urls:
                    QuestionImage.objects.create(question=instance, img_url=old_url)
                # 업로드 실패한 새 s3 URL 삭제
                for new_url in new_s3_urls:
                    s3_uploader.delete_file(new_url)
                # 예외 발생 (필요에 따라 직접 에러 처리)
                raise APIException("이미지 업로드에 실패했습니다. 기존 이미지는 보존됩니다.")

        instance.save()
        return instance


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


# 질문 카테고리 목록 조회
class ParentQnACategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name"]


# 질의응답 카테고리 직렬화
class MinorQnACategorySerializer(serializers.ModelSerializer):
    parent_ctg = ParentQnACategorySerializer(source="parent", read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent_ctg", "category_type"]


# 질의응답 카테고리 중분류 직렬화
class MiddleQnACategorySerializer(MinorQnACategorySerializer):
    child_categories = MinorQnACategorySerializer(source="subcategories", many=True, read_only=True)
    parent_ctg = ParentQnACategorySerializer(source="parent", read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent_ctg", "category_type", "child_categories"]


# 질의응답 카테고리 대분류 직렬화
class MajorQnACategorySerializer(MinorQnACategorySerializer):
    child_categories = MiddleQnACategorySerializer(source="subcategories", many=True, read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "category_type", "child_categories"]
