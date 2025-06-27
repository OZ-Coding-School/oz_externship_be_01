from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from apps.community.models import Post
from apps.community.serializers.attachment_serializers import PostImageResponseSerializer, \
    PostAttachmentResponseSerializer
from apps.community.serializers.comment_serializer import CommentResponseSerializer
from apps.community.serializers.post_author_serializers import AuthorSerializer
from apps.community.serializers.attachment_serializers import PostAttachmentRequestSerializer

# 게시글 목록
class PostListSerializer(serializers.ModelSerializer[Post]):
    category = serializers.SerializerMethodField()

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "공지사항"},
            },
        }
    )
    def get_category(self, obj: Any) -> dict[str, Any]:
        category = getattr(obj, "category", None)
        if category:
            category_id = category.get("id") if isinstance(category, dict) else getattr(category, "id", None)
            return {"id": category_id, "name": "공지사항" if category_id == 1 else f"카테고리 {category_id}"}
        return {"id": None, "name": "없음"}


    class Meta:
        model = Post
        fields = (
            'id',
            'category',
            'author',
            'title',
            'view_count',
            'likes_count',
            'comment_count',
            'is_notice',
            'is_visible',
            'created_at'
        )

        read_only_fields = fields

# 게시글 디테일
class PostDetailSerializer(serializers.ModelSerializer[Post]):
    category = serializers.SerializerMethodField()
    author = AuthorSerializer()
    attachments = PostAttachmentResponseSerializer(many=True, required=False, default=[])
    images = PostImageResponseSerializer(many=True, required=False, default=[])
    comments = CommentResponseSerializer(many=True, required=False, default=[])

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "공지사항"},
            },
        }
    )
    def get_category(self, obj: Any) -> dict[str, Any]:
        category = getattr(obj, "category", None)
        if category:
            category_id = category.get("id") if isinstance(category, dict) else getattr(category, "id", None)
            return {"id": category_id, "name": "공지사항" if category_id == 1 else f"카테고리 {category_id}"}
        return {"id": None, "name": "없음"}

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
class PostUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    is_visible = serializers.BooleanField(required=False)
    attachments = PostAttachmentRequestSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ("title", "content", "category", "is_visible", "attachments")