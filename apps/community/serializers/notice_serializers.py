import uuid

from rest_framework import serializers

from apps.community.models import Post, PostAttachment, PostCategory, PostImage
from apps.community.serializers.attachment_serializers import (
    PostAttachmentResponseSerializer,
    PostImageResponseSerializer,
)
from apps.community.serializers.category_serializers import (
    CategoryDetailResponseSerializer,
)
from apps.community.serializers.comment_serializers import CommentResponseSerializer
from apps.community.serializers.fields import FileListField
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader
from core.utils.validators import validate_uploaded_files, BLOCKED_ATTACHMENT_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS


# 공지 사항 등록
class NoticeCreateSerializer(serializers.ModelSerializer[Post]):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    is_notice = serializers.BooleanField(required=True)
    attachments = FileListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )
    images = FileListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
    )

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

    def validate_attachments(self, attachments):
        validate_uploaded_files(
            files=attachments,
            max_count=3,
            max_size_mb= 10,
            blocked_extensions=BLOCKED_ATTACHMENT_EXTENSIONS,
            field_name="attachments",
        )
        return attachments

    def validate_images(self, images):
        validate_uploaded_files(
            files=images,
            max_count=5,
            max_size_mb= 5,
            allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
            field_name="images",
        )
        return images

    def create(self, validated_data):
        attachments = self.context["request"].FILES.getlist("attachments")
        images = self.context["request"].FILES.getlist("images")

        validated_data.pop("attachments", [])
        validated_data.pop("images", [])
        validated_data["category"], _ = PostCategory.objects.get_or_create(name="공지사항")
        validated_data["author"] = self.context["request"].user

        uploader = S3Uploader()

        uploaded_s3_keys = []

        try:
            success_attachments = []
            for file in attachments:
                unique_name = f"{uuid.uuid4().hex[:6]}_{file.name}"
                s3_key = f"oz_externship_be/community/attachments/{unique_name}"
                url = uploader.upload_file(file, s3_key)
                if not url:
                    raise serializers.ValidationError(f"[첨부파일 업로드 실패] {file.name}")
                uploaded_s3_keys.append(url)
                success_attachments.append(PostAttachment(file_url=url, file_name=file.name))

            success_images = []
            for image in images:
                unique_name = f"{uuid.uuid4().hex[:6]}_{image.name}"
                s3_key = f"oz_externship_be/community/images/{unique_name}"
                url = uploader.upload_file(image, s3_key)
                if not url:
                    raise serializers.ValidationError(f"[이미지 업로드 실패] {image.name}")
                uploaded_s3_keys.append(url)
                success_images.append(PostImage(image_url=url, image_name=image.name))

            post = Post.objects.create(**validated_data)
            for attachment_instance in success_attachments:
                attachment_instance.post = post
            for image_instance in success_images:
                image_instance.post = post

            PostAttachment.objects.bulk_create(success_attachments)
            PostImage.objects.bulk_create(success_images)

            return post

        except Exception as e:
            for s3_url in uploaded_s3_keys:
                try:
                    uploader.delete_file(s3_url)
                except Exception:
                    pass
            raise serializers.ValidationError({"non_field_errors": [f"파일 업로드 중 오류가 발생했습니다: {e}"]})

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
