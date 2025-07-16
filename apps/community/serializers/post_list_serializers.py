from rest_framework import serializers

from apps.community.models import Post
from apps.community.serializers.attachment_serializers import (
    PostImageResponseSerializer,
)
from apps.community.serializers.category_serializers import (
    CategoryListResponseSerializer,
)
from apps.community.serializers.post_author_serializers import AuthorSerializer


class PostListViewSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategoryListResponseSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "summary",
            "thumbnail",
            "category",
            "title",
            "created_at",
            "likes_count",
            "comment_count",
            "view_count",
        ]

    def get_thumbnail(self, obj):
        image = obj.images.first()
        if image is not None:
            return PostImageResponseSerializer(image).data
        return None

    def get_summary(self, obj):
        content = obj.content or ""
        return content[:50] + "..." if len(content) > 50 else content
