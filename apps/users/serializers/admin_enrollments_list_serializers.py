from rest_framework import serializers

from apps.users.models import StudentEnrollmentRequest


# 요청
class EnrollmentRequestIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), help_text="승인할 수강생 등록 신청의 ID 리스트")


# 응답
class ApprovalResponseSerializer(serializers.Serializer):
    approved_ids = serializers.ListField(child=serializers.IntegerField(), help_text="승인된 수강신청 ID 목록")
    message = serializers.CharField(help_text="처리 결과 요약 메시지")


# Admin 전용 수강신청 목록
class AdminEnrollmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_birthday = serializers.DateField(source="user.birthday", read_only=True)
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
