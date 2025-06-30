from rest_framework import serializers

from ..models import ChatbotMessage, ChatbotSession


class ChatbotSessionSerializer(serializers.ModelSerializer[ChatbotSession]):
    class Meta:
        model = ChatbotSession
        fields = [
            "id",
            "user",
            "question",
            "socket_id",
            "status",
            "rejection_reason",
            "chat_count",
            "is_waiting_reply",
            "created_at",
            "disconnected_at",
        ]
        read_only_fields = ["id", "created_at", "disconnected_at"]


class ChatbotMessageSerializer(serializers.ModelSerializer[ChatbotMessage]):
    class Meta:
        model = ChatbotMessage
        fields = ["id", "session", "sender_type", "content", "is_question_related", "created_at"]
        read_only_fields = ["id", "created_at"]
