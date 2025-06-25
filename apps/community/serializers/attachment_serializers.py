from typing import Any

from rest_framework import serializers


# 첨부 파일
class AttachmentSerializer(serializers.Serializer[Any]):  # 실제 저장할 경우 [PostAttachment]
    file_url = serializers.URLField()
    file_name = serializers.CharField(max_length=255)


# 이미지
class ImageSerializer(serializers.Serializer[Any]):  # 실제 저장할 경우 [PostImage]
    image_url = serializers.URLField()
