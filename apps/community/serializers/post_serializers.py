from rest_framework import serializers

from apps.community.models import Post, PostCategory
from apps.community.serializers.attachment_serializers import (
    PostAttachmentResponseSerializer,
    PostImageResponseSerializer,
)
from apps.community.serializers.comment_serializers import CommentResponseSerializer
from apps.community.serializers.category_serializers import CategoryDetailResponseSerializer
from apps.community.serializers.post_author_serializers import AuthorSerializer


# 게시글 목록
class PostListSerializer(serializers.ModelSerializer[Post]):
    category = CategoryDetailResponseSerializer()
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = (
            "id",
            "category",
            "author",
            "title",
            "view_count",
            "likes_count",
            "comment_count",
            "is_notice",
            "is_visible",
            "created_at",
        )
        read_only_fields = fields

# 게시글 디테일
class PostDetailSerializer(serializers.ModelSerializer[Post]):
    category = CategoryDetailResponseSerializer()
    author = AuthorSerializer()
    attachments = PostAttachmentResponseSerializer(many=True, required=False, default=[])
    images = PostImageResponseSerializer(many=True, required=False, default=[])
    comments = CommentResponseSerializer(many=True, required=False, default=[])

    class Meta:
        model = Post
        fields = (
            "id",
            "category",
            "author",
            "title",
            "content",
            "view_count",
            "likes_count",
            "comment_count",
            "is_visible",
            "is_notice",
            "attachments",
            "images",
            "comments",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


# 게시글 수정
class PostUpdateSerializer(serializers.ModelSerializer[Post]):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=PostCategory.objects.all(), required=False)
    is_visible = serializers.BooleanField(required=False)
    attachments = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True, allow_empty=True
    )
    images = serializers.ListField(child=serializers.ImageField(), required=False, write_only=True, allow_empty=True)

    class Meta:
        model = Post
        fields = ("title", "content", "category", "is_visible", "attachments", "images")

    def update(self, instance, validated_data):
        validated_data.pop("attachments", None)
        validated_data.pop("images", None)

        return super().update(instance, validated_data)
