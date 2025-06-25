from typing import Any

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment, AnswerImage


class AnswerCreateSerializer(serializers.ModelSerializer[Answer]):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)

    class Meta:
        model = Answer
        fields = ["content", "images"]

    def create(self, validated_data: dict[str, Any]) -> Answer:
        images = validated_data.pop("images", [])
        # answer 모델에 직접 이미지를 저장하지 않기 때문에 validate_data에서 일단 꺼내서 answer create
        answer = Answer.objects.create(**validated_data)
        return answer


class AnswerUpdateSerializer(serializers.ModelSerializer[Answer]):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    delete_image_ids = serializers.CharField(required=False)

    class Meta:
        model = Answer
        fields = ["content", "images", "delete_image_ids"]

    def update(self, instance: Answer, validated_data: dict[str, Any]) -> Answer:
        # 컨텐츠 업데이트만 구현, 이미지 수정, 삭제는 나중에
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class AnswerCommentCreateSerializer(serializers.ModelSerializer[AnswerComment]):
    class Meta:
        model = AnswerComment
        fields = ["content"]

    def validate_content(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError("댓글 내용은 500자 이하로 입력해야 합니다.")
        return value
