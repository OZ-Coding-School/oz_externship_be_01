from typing import Any

from rest_framework import serializers


# 첨부 파일 요청
class PostAttachmentRequestSerializer(serializers.Serializer[Any]):  # 실제 저장할 경우 [PostAttachment]
    file = serializers.FileField(write_only=True)


# 첨부 파일 응답
class PostAttachmentResponseSerializer(serializers.Serializer[Any]):
    file_url = serializers.URLField(read_only=True)
    file_name = serializers.CharField(read_only=True)


# 이미지 요청
class PostImageRequestSerializer(serializers.Serializer[Any]):  # 실제 저장할 경우 [PostImage]
    image = serializers.ImageField(write_only=True)


# 이미지 응답
class PostImageResponseSerializer(serializers.Serializer[Any]):  # 실제 저장할 경우 [PostImage]
    image_url = serializers.URLField(read_only=True)
    image_name = serializers.CharField(read_only=True)
