import uuid

from rest_framework import serializers

from apps.community.models import Post, PostAttachment, PostCategory, PostImage
from apps.community.serializers.attachment_serializers import (
    PostAttachmentResponseSerializer,
    PostImageResponseSerializer,
)
from apps.community.serializers.comment_serializers import CommentResponseSerializer
from apps.community.serializers.category_serializers import CategoryDetailResponseSerializer
from apps.community.serializers.fields import FileListField
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader
from core.utils.validators import (
    ALLOWED_IMAGE_EXTENSIONS,
    BLOCKED_ATTACHMENT_EXTENSIONS,
    validate_uploaded_files,
)


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
    attachments = FileListField(child=serializers.FileField(), required=False, write_only=True, allow_empty=True)
    images = FileListField(child=serializers.ImageField(), required=False, write_only=True, allow_empty=True)

    class Meta:
        model = Post
        fields = ("title", "content", "category", "is_visible", "attachments", "images")

    def validate_attachments(self, attachments):
        validate_uploaded_files(
            files=attachments,
            max_count=3,
            max_size_mb=10,
            blocked_extensions=BLOCKED_ATTACHMENT_EXTENSIONS,
            field_name="attachments",
        )
        return attachments

    def validate_images(self, images):
        validate_uploaded_files(
            files=images,
            max_count=5,
            max_size_mb=5,
            allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
            field_name="images",
        )
        return images

    def update(self, instance, validated_data: dict) -> Post:
        uploader = S3Uploader()
        request_files = self.context["request"].FILES

        uploaded_s3_keys = []

        try:
            new_attachments, new_images = [], []

            if "attachments" in self.initial_data:
                attachments = request_files.getlist("attachments")

                for file in attachments:
                    unique_file_name = f"{uuid.uuid4().hex[:6]}_{file.name}"
                    s3_key = f"oz_externship_be/community/attachments/{unique_file_name}"
                    url = uploader.upload_file(file, s3_key)
                    if not url:
                        raise serializers.ValidationError({"attachments": [f"{file.name} 업로드 실패"]})
                    uploaded_s3_keys.append(url)
                    new_attachments.append(PostAttachment(post=instance, file_url=url, file_name=file.name))

            if "images" in self.initial_data:
                images = request_files.getlist("images")

                for image in images:
                    unique_name = f"{uuid.uuid4().hex[:6]}_{image.name}"
                    s3_key = f"oz_externship_be/community/images/{unique_name}"
                    url = uploader.upload_file(image, s3_key)
                    if not url:
                        raise serializers.ValidationError({"images": [f"{image.name} 업로드 실패"]})
                    uploaded_s3_keys.append(url)
                    new_images.append(PostImage(post=instance, image_url=url, image_name=image.name))

                for old in instance.attachments.all():
                    uploader.delete_file(old.file_url)
                instance.attachments.all().delete()
                PostAttachment.objects.bulk_create(new_attachments)

                for old in instance.images.all():
                    uploader.delete_file(old.image_url)
                instance.images.all().delete()
                PostImage.objects.bulk_create(new_images)

            validated_data.pop("attachments", [])
            validated_data.pop("images", [])

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance

        except Exception as e:
            for s3_url in uploaded_s3_keys:
                try:
                    uploader.delete_file(s3_url)
                except Exception:
                    pass
            raise serializers.ValidationError({"non_field_errors": [f"파일 업로드 중 오류가 발생했습니다: {e}"]})
