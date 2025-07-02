from typing import Any

from rest_framework import serializers

from apps.users.models import StudentEnrollmentRequest


# 요청
class MockEnrollmentSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField(min_value=1, help_text="수강 신청 ID")
    status = serializers.ChoiceField(
        choices=StudentEnrollmentRequest.EnrollmentStatus.choices, help_text="현재 상태 (PENDING, APPROVED, REJECTED)"
    )


class RejectEnrollmentRequestSerializer(serializers.Serializer):
    enrollment_request_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, help_text="반려할 수강생 등록 신청 ID 목록"
    )


# 반려 응답
class RejectionResponseSerializer(serializers.Serializer[Any]):
    rejected_ids = serializers.ListField(child=serializers.IntegerField(), help_text="반려 처리된 수강신청 ID")
    skipped_ids = serializers.ListField(child=serializers.IntegerField(), help_text="이미 반려되어 건너뛴 ID")
    downgraded_user_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="권한이 General로 롤백된 ID"
    )
    deleted_permission_ids = serializers.ListField(child=serializers.IntegerField(), help_text="수강 권한 삭제된 ID")
    message = serializers.CharField(help_text="처리 결과 메시지")
    mock_processed_at = serializers.DateTimeField(help_text="Mock 처리 일시")
