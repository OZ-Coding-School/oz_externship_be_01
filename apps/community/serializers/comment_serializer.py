from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers

from apps.community.models import Comment, Post

User = get_user_model()


class UserCommentSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = User
        fields = ("id", "nickname")


class CommentResponseSerializer(serializers.ModelSerializer[Any]):
    author = UserCommentSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
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
        fields = ["content"]
