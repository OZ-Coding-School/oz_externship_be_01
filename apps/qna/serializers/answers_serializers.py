from typing import Any

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment, AnswerImage
from apps.users.models import User


class AuthorSerializer(serializers.ModelSerializer[User]):
    # 작성자 정보를 위한 별도 시리얼라이저
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "role"]


class AnswerListSerializer(serializers.ModelSerializer[Answer]):
    author = AuthorSerializer(read_only=True)

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


class AnswerCreateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()


class AnswerUpdateSerializer(serializers.ModelSerializer[Answer]):
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = Answer
        fields = ["content", "image_files", "image_urls"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()


class AnswerCommentCreateSerializer(serializers.ModelSerializer[AnswerComment]):

    # TODO : 답변 id, 댓글 id(몇번째 댓글인지) 추가 예정
    class Meta:
        model = AnswerComment
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError("댓글 내용은 500자 이하로 입력해야 합니다.")
        return value
