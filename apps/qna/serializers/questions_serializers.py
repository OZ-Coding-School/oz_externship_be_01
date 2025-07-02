from typing import Any

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory, QuestionImage


class SafeImageListField(serializers.ListField):
    def to_internal_value(self, data):
        # DRF 내부에서 "" 도 `child.to_internal_value()` 하려다 죽기 때문에,
        # 여기서 "" 필터링 해줘야 함
        if isinstance(data, list):
            # 빈 문자열/None은 제거
            data = [item for item in data if item not in ["", None]]
        return super().to_internal_value(data)


# 질문 이미지
class QuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


# 질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer):
    image_files = SafeImageListField(
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

        # TODO: depth 필드가 생기면 이 조건은 수정 필요
        if category.parent is None or category.parent.parent is None:
            raise serializers.ValidationError("소분류 카테고리만 선택할 수 있습니다.")

        return category

    def validate_image_files(self, value: list[UploadedFile]) -> list[UploadedFile]:
        if len(value) > 5:
            raise serializers.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
        return value

    def create(self, validated_data: dict[str, Any]) -> Question:
        image_files: list[UploadedFile] = validated_data.pop("image_files", [])
        category: QuestionCategory = validated_data.pop("category_id")
        user = self.context["request"].user  # TODO: 사용자 처리 검토

        question = Question.objects.create(category=category, author=user, **validated_data)

        for img in image_files:
            # TODO: 외부 스토리지 정책 확인
            path = default_storage.save(f"questions/{img.name}", img)
            url = default_storage.url(path)
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
