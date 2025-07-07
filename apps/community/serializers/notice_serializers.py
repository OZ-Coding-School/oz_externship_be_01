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
from apps.community.serializers.comment_serializer import CommentResponseSerializer
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader


# 공지 사항 등록
class NoticeCreateSerializer(serializers.ModelSerializer[Post]):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    is_notice = serializers.BooleanField(required=True)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )
    images = serializers.ListField(
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

    def create(self, validated_data):
        attachments = self.context["request"].FILES.getlist("attachments")
        images = self.context["request"].FILES.getlist("images")

        validated_data.pop("attachments", [])
        validated_data.pop("images", [])

        validated_data["category"], _ = PostCategory.objects.get_or_create(name="공지사항")
        validated_data["author"] = self.context["request"].user

        post = Post.objects.create(**validated_data)

        uploader = S3Uploader()

        # 첨부파일 S3 업로드
        for file in attachments:
            unique_file_name = f"{uuid.uuid4().hex[:6]}_{file.name}"
            s3_key = f"oz_externship_be/community/attachments/{unique_file_name}"
            url = uploader.upload_file(file, s3_key)
            if url:
                PostAttachment.objects.create(post=post, file_url=url, file_name=file.name)

        # 이미지 S3 업로드
        for image in images:
            unique_image_name = f"{uuid.uuid4().hex[:6]}_{image.name}"
            s3_key = f"oz_externship_be/community/images/{unique_image_name}"
            url = uploader.upload_file(image, s3_key)
            if url:
                PostImage.objects.create(post=post, image_url=url, image_name=image.name)

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
