import uuid

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.community.models import Post, PostAttachment, PostCategory, PostImage
from apps.community.serializers.fields import FileListField
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader
from core.utils.validators import (
    ALLOWED_IMAGE_EXTENSIONS,
    BLOCKED_ATTACHMENT_EXTENSIONS,
    validate_uploaded_files,
)


class PostCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    author = AuthorSerializer(read_only=True)
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
        fields = [
            "category_id",
            "author",
            "title",
            "content",
            "is_visible",
            "is_notice",
            "attachments",
            "images",
        ]

    def validate_category_id(self, value):
        if not PostCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("category_id: 존재하지 않는 카테고리입니다.")
        return value

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

    # def validate_author_id(self, value):
    # if not User.objects.filter(id=value).exists():
    # raise serializers.ValidationError("author_id: 존재하지 않는 사용자입니다.")
    # return value

    def create(self, validated_data):
        images = self.context["request"].FILES.getlist("images")
        attachments = self.context["request"].FILES.getlist("attachments")
        validated_data.pop("attachments", [])
        validated_data.pop("images", [])
        validated_data["author"] = self.context["request"].user
        validated_data["category"] = get_object_or_404(PostCategory, id=validated_data.pop("category_id"))

        uploader = S3Uploader()

        # 첨부파일 업로드
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
