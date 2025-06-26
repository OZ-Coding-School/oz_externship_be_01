from typing import Any, Dict

from rest_framework import serializers


class CommentDeleteResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    detail = serializers.CharField(help_text="삭제 실패 시 반환되는 오류 메시지")
