from typing import Any, List, Type

from rest_framework import serializers

from apps.users.models import StudentEnrollmentRequest


# 요청용 시리얼라이저
class EnrollmentRequestIdsSerializer(serializers.Serializer[Any]):
    ids = serializers.ListField(  # ✅ ListField는 제네릭 X
        child=serializers.IntegerField(), help_text="승인할 수강생 등록 신청의 ID 리스트"
    )


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


class AdminEnrollmentSerializer(serializers.ModelSerializer):
    # 유저 관련 필드 (이름, 이메일, 생년월일)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_birthday = serializers.DateField(source="user.birthday", read_only=True)

    # 과정명과 기수명
    course_name = serializers.CharField(source="generation.course.name", read_only=True)
    generation_name = serializers.CharField(source="generation.name", read_only=True)

    class Meta:
        model = StudentEnrollmentRequest
        fields = [
            "id",
            "user_name",
            "user_email",
            "user_birthday",
            "course_name",
            "generation_name",
            "status",
            "accepted_at",
            "created_at",
            "updated_at",
        ]
