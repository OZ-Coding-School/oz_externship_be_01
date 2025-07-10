from typing import Any, Dict

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment, AnswerImage
from apps.qna.serializers.images_serializers import AnswerImageMixin, ImageURLSerializer
from apps.users.models import User

# View는 HTTP 처리, Serializer는 데이터 처리


class AuthorSerializer(serializers.ModelSerializer[User]):
    # 작성자 정보를 위한 별도 시리얼라이저
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "role"]


class AnswerCommentListSerializer(serializers.ModelSerializer[AnswerComment]):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComment
        fields = ["id", "answer_id", "author", "content", "created_at", "updated_at"]


class AnswerListSerializer(serializers.ModelSerializer[Answer]):
    author = AuthorSerializer(read_only=True)
    comments = AnswerCommentListSerializer(many=True, read_only=True)
    img_url = ImageURLSerializer(many=True, read_only=True)

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
            "img_url",
            "comments",
        ]


class AnswerCreateSerializer(AnswerImageMixin, serializers.ModelSerializer[Answer]):

    class Meta:
        model = Answer
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()

    def create(self, validated_data: Dict[str, Any]) -> Answer:
        """Answer 생성 및 이미지 URL 추출하여 저장"""
        answer = super().create(validated_data)

        content = validated_data["content"]

        # content에서 이미지 URL 추출
        image_urls = self._extract_image_urls_from_content(content)

        # AnswerImage 생성 (DB 저장만)
        self._save_answer_images(answer, image_urls)

        return answer


class AnswerUpdateSerializer(AnswerImageMixin, serializers.ModelSerializer[Answer]):

    class Meta:
        model = Answer
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        # 마크다운 형식 지원, 빈 내용 방지
        if not value or not value.strip():
            raise serializers.ValidationError("답변 내용을 입력해주세요.")
        return value.strip()

    def update(self, instance, validated_data):
        # 기존 AnswerImage들 삭제
        AnswerImage.objects.filter(answer=instance).delete()

        # Answer 업데이트
        answer = super().update(instance, validated_data)

        content = validated_data["content"]

        # content에서 이미지 URL 추출
        image_urls = self._extract_image_urls_from_content(content)

        # 새로운 AnswerImage 생성
        self._save_answer_images(answer, image_urls)

        return answer


class AnswerCommentCreateSerializer(serializers.ModelSerializer[AnswerComment]):

    # TODO : 답변 id, 댓글 id(몇번째 댓글인지) 추가 예정
    class Meta:
        model = AnswerComment
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError("댓글 내용은 500자 이하로 입력해야 합니다.")
        return value
