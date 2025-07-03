from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.community.models import Post, PostAttachment, PostCategory, PostImage

User = get_user_model()


class PostCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    attachments = serializers.ListField(child=serializers.FileField(), max_length=5, write_only=True, required=False)
    images = serializers.ListField(child=serializers.ImageField(), max_length=5, write_only=True, required=False)

    class Meta:
        model = Post
        fields = [
            "category_id",
            "author_id",
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

    def validate_author_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("author_id: 존재하지 않는 사용자입니다.")
        return value

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        images_data = validated_data.pop("images", [])
        try:
            category = PostCategory.objects.get(id=validated_data.pop("category_id"))
            author = User.objects.get(id=validated_data.pop("author_id"))
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        except PostCategory.DoesNotExist:
            raise serializers.ValidationError("category not found.")

        post = Post.objects.create(category=category, author=author, **validated_data)

        for attachment in attachments_data:
            PostAttachment.objects.create(
                post=post, file_url=f"media/community/posts/{attachment.name}", file_name=attachment.name
            )

        for image in images_data:
            PostImage.objects.create(post=post, img_url=f"media/community/posts/{image.name}")

        return post
