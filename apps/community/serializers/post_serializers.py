from rest_framework import serializers
from apps.community.models import Post
from apps.community.serializers.post_author_serializers import AuthorSerializer


class PostListSerializer(serializers.ModelSerializer[Post]):

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
