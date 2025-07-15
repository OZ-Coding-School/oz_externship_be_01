from typing import Any

from django.db import transaction
from rest_framework import serializers

from apps.users.models import User

from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.qna.serializers.answers_serializers import AnswerListSerializer
from apps.qna.serializers.images_serializers import QuestionImageMixin


# 질문 이미지
class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


# 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer, QuestionImageMixin):
    images = QuestionImageSerializer(many=True, read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = ["title", "content", "category_id", "images"]

    def validate_category_id(self, value):
        try:
            category = QuestionCategory.objects.get(pk=value)
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("해당 카테고리가 존재하지 않습니다.")
        if category.category_type != "minor":
            raise serializers.ValidationError("카테고리는 소분류만 가능합니다.")
        return category

    def create(self, validated_data):
        content = validated_data["content"]
        image_urls = list(dict.fromkeys(self._extract_image_urls_from_content(content)))
        if len(image_urls) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
        category = validated_data.pop("category_id")
        author = validated_data.pop("author", None)

        with transaction.atomic():
            question = Question.objects.create(category=category, author=author, **validated_data)
            self._save_question_images(question, image_urls)
        return question


# 질문 수정
class QuestionUpdateSerializer(serializers.ModelSerializer, QuestionImageMixin):
    images = QuestionImageSerializer(many=True, read_only=True)
    category_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Question
        fields = ["category", "category_id", "title", "content", "images"]
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
        return category

    def update(self, instance, validated_data):
        for field in ["title", "content"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if "category_id" in validated_data:
            instance.category = validated_data["category_id"]  # 이미 객체!

        if "content" in validated_data:
            content = validated_data["content"]
            image_urls = list(dict.fromkeys(self._extract_image_urls_from_content(content)))  # 순서 보존
            if len(image_urls) > 5:
                raise serializers.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
            instance.images.all().delete()
            self._save_question_images(instance, image_urls)

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
class AuthorInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]
        read_only_fields = fields


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
class QuestionDetailSerializer(serializers.ModelSerializer):
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
