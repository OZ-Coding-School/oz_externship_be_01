from typing import Any

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment, AnswerImage


class AnswerListSerializer(serializers.ModelSerializer[Answer]):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "id",
            "question_id",
            "author",
            "content",
            "is_adopted",
            "created_at",
            "updated_at",
        ]

    def get_author(self, obj: Answer) -> dict[str, Any]:
        return {
            "id": obj.author.id,
            "nickname": obj.author.nickname,
            "profile_image": getattr(obj.author, "profile_image_url", ""),
            "role": getattr(obj.author, "role", ""),
        }


class AnswerCreateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]


class AnswerUpdateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]


class AnswerCommentCreateSerializer(serializers.ModelSerializer[AnswerComment]):

    # TODO : 답변 id, 댓글 id(몇번째 댓글인지) 추가 예정
    class Meta:
        model = AnswerComment
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError("댓글 내용은 500자 이하로 입력해야 합니다.")
        return value
