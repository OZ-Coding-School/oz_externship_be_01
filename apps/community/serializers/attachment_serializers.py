from rest_framework import serializers

from apps.community.models import PostAttachment, PostImage


# 첨부 파일 응답
class PostAttachmentResponseSerializer(serializers.ModelSerializer):
    file_url = serializers.URLField(read_only=True)
    file_name = serializers.CharField(read_only=True)

    class Meta:
        model = PostAttachment
        fields = ["id", "file_url", "file_name"]


# 이미지 응답
class PostImageResponseSerializer(serializers.ModelSerializer):  # 실제 저장할 경우 [PostImage]
    image_url = serializers.URLField(read_only=True)
    image_name = serializers.CharField(read_only=True)

    class Meta:
        model = PostImage
        fields = ["id", "image_url", "image_name"]
