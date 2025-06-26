from typing import List

from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory, QuestionImage


# 질문 이미지
class QuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


# 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    images = QuestionImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = ["category", "category_id", "title", "content", "images", "image_files"]
        read_only_fields = ["category"]


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


# 질문 목록 조회
class QuestionListSerializer(serializers.ModelSerializer[Question]):
    images = QuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]


# 질문 상세 조회
class QuestionDetailSerializer(serializers.ModelSerializer[Question]):
    images = QuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]
