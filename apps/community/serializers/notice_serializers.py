from rest_framework import serializers

from apps.community.models import Post, PostCategory, PostAttachment, PostImage
from apps.community.serializers.attachment_serializers import (
    PostAttachmentRequestSerializer,
    PostAttachmentResponseSerializer,
    PostImageRequestSerializer,
    PostImageResponseSerializer,
)
from apps.community.serializers.category_serializers import CategoryDetailResponseSerializer
from apps.community.serializers.comment_serializer import CommentResponseSerializer
from apps.community.serializers.post_author_serializers import AuthorSerializer


# 공지 사항 등록
class NoticeCreateSerializer(serializers.ModelSerializer[Post]):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    is_notice = serializers.BooleanField(required=True)
    attachments = PostAttachmentRequestSerializer(many=True, required=False, write_only=True)
    images = PostImageRequestSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "is_notice",
            "is_visible",
            "attachments",
            "images",
        )

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        images_data = validated_data.pop("images", [])

        try:
            category = PostCategory.objects.get(name="공지사항")
        except PostCategory.DoesNotExist:
            raise serializers.ValidationError("공지사항 카테고리가 존재하지 않습니다.")

        validated_data["category"] = category
        validated_data["author"] = self.context["request"].user

        post = Post.objects.create(**validated_data)

        for attachment in attachments_data:
            PostAttachment.objects.create(post=post, **attachment)

        for image in images_data:
            PostImage.objects.create(post=post, **image)

        return post

# 공지 사항 응답
class NoticeResponseSerializer(serializers.ModelSerializer[Post]):
    attachments = PostAttachmentResponseSerializer(many=True, required=False, default=[])
    images = PostImageResponseSerializer(many=True, required=False, default=[])
    category = CategoryDetailResponseSerializer()
    author = AuthorSerializer()
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
