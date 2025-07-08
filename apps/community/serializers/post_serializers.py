import uuid

from rest_framework import serializers

from apps.community.models import Post, PostCategory, PostAttachment, PostImage
from apps.community.serializers.attachment_serializers import (
    PostAttachmentResponseSerializer,
    PostImageResponseSerializer,
)
from apps.community.serializers.comment_serializers import CommentResponseSerializer
from apps.community.serializers.category_serializers import CategoryDetailResponseSerializer
from apps.community.serializers.fields import FileListField
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader


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
    attachments = FileListField(
        child=serializers.FileField(), required=False, write_only=True, allow_empty=True
    )
    images = FileListField(child=serializers.ImageField(), required=False, write_only=True, allow_empty=True)

    class Meta:
        model = Post
        fields = ("title", "content", "category", "is_visible", "attachments", "images")

    def update(self, instance, validated_data: dict) -> Post:
        uploader = S3Uploader()
        request_files = self.context["request"].FILES

        # 첨부파일 처리
        if "attachments" in self.initial_data:
            for attachment in instance.attachments.all():
                uploader.delete_file(attachment.file_url)
            instance.attachments.all().delete()

            for file in request_files.getlist("attachments"):
                unique_file_name = f"{uuid.uuid4().hex[:6]}_{file.name}"
                s3_key = f"oz_externship_be/community/attachments/{unique_file_name}"
                url = uploader.upload_file(file, s3_key)
                if url:
                    PostAttachment.objects.create(post=instance, file_url=url, file_name=file.name)

        # 이미지 처리
        if "images" in self.initial_data:
            for image in instance.images.all():
                uploader.delete_file(image.image_url)
            instance.images.all().delete()

            for image in request_files.getlist("images"):
                unique_image_name = f"{uuid.uuid4().hex[:6]}_{image.name}"
                s3_key = f"oz_externship_be/community/images/{unique_image_name}"
                url = uploader.upload_file(image, s3_key)
                if url:
                    PostImage.objects.create(post=instance, image_url=url, image_name=image.name)

        validated_data.pop("attachments", [])
        validated_data.pop("images", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
