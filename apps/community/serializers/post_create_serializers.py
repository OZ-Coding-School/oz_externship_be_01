import uuid

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.community.models import Post, PostAttachment, PostCategory, PostImage
from apps.community.serializers.post_author_serializers import AuthorSerializer
from core.utils.s3_file_upload import S3Uploader


class PostCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    author = AuthorSerializer(read_only=True)
    attachments = serializers.ListField(
        child=serializers.FileField(), max_length=5, write_only=True, required=False, default=list
    )
    images = serializers.ListField(
        child=serializers.ImageField(), max_length=5, write_only=True, required=False, default=list
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

    # def validate_author_id(self, value):
    # if not User.objects.filter(id=value).exists():
    # raise serializers.ValidationError("author_id: 존재하지 않는 사용자입니다.")
    # return value

    def create(self, validated_data):
        request = self.context.get("request")
        attachments_data = validated_data.pop("attachments", [])
        images_data = validated_data.pop("images", [])
        author = request.user
        category = PostCategory.objects.get(id=validated_data.pop("category_id"))
        # validated_data['author'] = self.context['request'].user
        post = Post.objects.create(category=category, author=author, **validated_data)
        uploader = S3Uploader()

        # 첨부파일 업로드
        for file in attachments_data:
            unique_file_name = f"{uuid.uuid4().hex[:6]}_{file.name}"
            s3_key = f"oz_externship_be/community/attachments/{unique_file_name}"
            url = uploader.upload_file(file, s3_key)
            if url:
                PostAttachment.objects.create(post=post, file_url=url, file_name=file.name)

        # 이미지 업로드
        for image in images_data:
            unique_image_name = f"{uuid.uuid4().hex[:6]}_{image.name}"
            s3_key = f"oz_externship_be/community/images/{unique_image_name}"
            url = uploader.upload_file(image, s3_key)
            if url:
                PostImage.objects.create(post=post, image_url=url, image_name=image.name)

        return post
