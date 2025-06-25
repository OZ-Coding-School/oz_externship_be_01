from typing import List

from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory


# 1. 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    image_urls = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Question
        fields = ["category_id", "title", "content", "image_urls"]

    def validate_category_id(self, value: int) -> int:
        try:
            cat = QuestionCategory.objects.get(id=value)
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("소분류 카테고리만 선택 가능합니다.")
        if not (cat.parent and cat.parent.parent):
            raise serializers.ValidationError("소분류 카테고리만 선택 가능합니다.")
        return value

    def validate_image_urls(self, value: List[str]) -> List[str]:
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지 업로드할 수 있습니다.")
        return value


# 2. 질문 수정
class QuestionUpdateSerializer(serializers.ModelSerializer[Question]):
    image_urls = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Question
        fields = ["title", "content", "category_id", "image_urls"]
        extra_kwargs = {
            "title": {"required": False},
            "content": {"required": False},
            "category_id": {"required": False},
        }

    def validate_category_id(self, value: int) -> int:
        try:
            cat = QuestionCategory.objects.get(id=value)
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("소분류 카테고리만 선택 가능합니다.")
        if not (cat.parent and cat.parent.parent):
            raise serializers.ValidationError("소분류 카테고리만 선택 가능합니다.")
        return value

    def validate_image_urls(self, value: List[str]) -> List[str]:
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지 업로드할 수 있습니다.")
        return value


# 3. 질문 목록 조회
class QuestionListSerializer(serializers.ModelSerializer[Question]):
    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at"]


# 4. 질문 상세 조회
class QuestionDetailSerializer(serializers.ModelSerializer[Question]):
    class Meta:
        model = Question
        fields = ["id", "title", "content", "images", "author", "category", "view_count", "created_at"]
