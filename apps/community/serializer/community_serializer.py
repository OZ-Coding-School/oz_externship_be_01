from typing import Any, Dict

from rest_framework import serializers


class CommentDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    detail = serializers.CharField(help_text="성공 또는 실패 메시지")
