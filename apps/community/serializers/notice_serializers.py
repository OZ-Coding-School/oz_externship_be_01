from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.community.models import Post
from apps.community.serializers.attachment_serializers import (
    PostAttachmentRequestSerializer,
    PostAttachmentResponseSerializer,
    PostImageRequestSerializer,
    PostImageResponseSerializer,
)


# 요청 데이터 검증
class NoticeCreateSerializer(serializers.ModelSerializer[Post]):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    category_id = serializers.IntegerField(write_only=True, required=True)
    is_notice = serializers.BooleanField(required=True)
    attachments = PostAttachmentRequestSerializer(many=True, required=False, write_only=True)
    images = PostImageRequestSerializer(many=True, required=False, write_only=True)

    def validate(self, value: dict[str, Any]) -> dict[str, Any]:
        if value.get("category_id") != 1:
            raise serializers.ValidationError(
                {"detail": {"code": "INVALID_CATEGORY", "message": "카테고리 '공지사항'에만 등록할 수 있습니다."}}
            )
        return value

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "category_id",
            "is_notice",
            "is_visible",
            "attachments",
            "images",
        )


# 응답 데이터용
class NoticeResponseSerializer(serializers.ModelSerializer[Post]):
    attachments = PostAttachmentResponseSerializer(many=True, read_only=True)
    images = PostImageResponseSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "category",
            "is_notice",
            "is_visible",
            "attachments",
            "images",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "title",
            "content",
            "is_notice",
            "is_visible",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "공지사항"},
            },
        }
    )
    def get_category(self, obj: Any) -> dict[str, Any]:
        category = getattr(obj, "category", None)

        if category:
            category_id = category.get("id") if isinstance(category, dict) else getattr(category, "id", None)
            return {"id": category_id, "name": "공지사항" if category_id == 1 else f"카테고리 {category_id}"}

        return {"id": None, "name": "없음"}
