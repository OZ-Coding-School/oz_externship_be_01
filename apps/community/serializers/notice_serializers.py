from typing import Any

from rest_framework import serializers

from apps.community.serializers.attachment_serializers import (
    AttachmentSerializer,
    ImageSerializer,
)


# 요청 데이터 검증
class NoticeCreateRequestSerializer(
    serializers.Serializer[Any]
):  # db에 저장하지 않기 때문에 [Any] -> 실제 저장할땐 [Post]
    title = serializers.CharField(write_only=True)
    content = serializers.CharField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    is_notice = serializers.BooleanField(write_only=True)
    is_visible = serializers.BooleanField(required=False, default=True, write_only=True)
    attachments = AttachmentSerializer(many=True, required=False, write_only=True)
    images = ImageSerializer(many=True, required=False, write_only=True)


# 응답 데이터용
class NoticeResponseSerializer(serializers.Serializer[Any]):  # db에 저장하지 않기 때문에 [Any] -> 실제 저장할땐 [Post]
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)
    category = serializers.DictField(read_only=True)
    is_notice = serializers.BooleanField(read_only=True)
    is_visible = serializers.BooleanField(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
