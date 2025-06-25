from typing import List

from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory


# 1. 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)
    image_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = ["category", "category_id", "title", "content", "image_urls", "image_files"]
        read_only_fields = ["category"]


# 2. 질문 수정
class QuestionUpdateSerializer(serializers.ModelSerializer[Question]):
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)
    image_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    category_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Question
        fields = ["category", "category_id", "title", "content", "image_urls", "image_files"]
        read_only_fields = ["category"]
        extra_kwargs = {
            "title": {"required": False},
            "content": {"required": False},
        }


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
