from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.community.models import Comment, CommentTags

User = get_user_model()


class UserCommentSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = ("id", "nickname")


class CommentTagSerializer(serializers.ModelSerializer[Any]):
    tagged_user = UserCommentSerializer(read_only=True)

    class Meta:
        model = CommentTags
        fields = ["tagged_user"]


class CommentResponseSerializer(serializers.ModelSerializer[Any]):
    author = UserCommentSerializer(read_only=True)
    tags = CommentTagSerializer(source="tags.all", many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
            "tags",
        )
        read_only_fields = ("created_at", "updated_at")


class CommentCreateSerializer(serializers.ModelSerializer[Any]):
    content = serializers.CharField(max_length=255)

    def validate(self, value: Any) -> Any:
        if not value:
            raise serializers.ValidationError("내용이 비어 있습니다.")
        return value

    class Meta:
        model = Comment
        fields = ["content", "author"]


class CommentUpdateSerializer(CommentCreateSerializer):

    def validate(self, value: Any) -> Any:
        if not value:
            raise serializers.ValidationError("변경할 내용이 없습니다.")
        return value
