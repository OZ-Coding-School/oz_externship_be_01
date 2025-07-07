from typing import Any

from rest_framework import serializers

from apps.users.models import StudentEnrollmentRequest


# 요청용 시리얼라이저
class EnrollmentRequestIdsSerializer(serializers.Serializer[Any]):
    enrollment_request_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="승인할 수강생 등록 신청의 ID 리스트"
    )

    def validate_ids(self, ids: list[int]) -> list[int]:
        if not ids:
            raise serializers.ValidationError("승인할 수강신청 ID 목록이 비어 있습니다.")
        return ids


# 승인 응답 시리얼라이저
class ApprovalResponseSerializer(serializers.Serializer[Any]):
    approved_ids = serializers.ListField(child=serializers.IntegerField(), help_text="mock 승인된 수강신청 ID 목록")
    message = serializers.CharField(help_text="처리 결과 요약 메시지")


# 수강생 등록 정보 시리얼라이저
class EnrollmentSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = StudentEnrollmentRequest
        fields = [
            "id",
            "user_id",
            "generation_id",
            "status",
            "accepted_at",
            "created_at",
            "updated_at",
        ]
