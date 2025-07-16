from rest_framework import serializers

from apps.courses.models import Generation
from apps.users.models import StudentEnrollmentRequest


class EnrollmentRequestCreateSerializer(serializers.ModelSerializer):
    generation = serializers.PrimaryKeyRelatedField(queryset=Generation.objects.all())

    class Meta:
        model = StudentEnrollmentRequest
        fields = ["generation"]

    def validate(self, data):
        user = self.context["request"].user
        generation = data["generation"]

        # 동일한 기수 신청 여부
        if StudentEnrollmentRequest.objects.filter(user=user, generation=generation).exists():
            raise serializers.ValidationError("이미 해당 기수에 신청한 이력이 있습니다.")

        # 기간이 겹치는 다른 신청 이력 존재 여부 검사
        start = generation.start_date
        end = generation.end_date

        # 겹치는 신청 내역 조회
        overlapping_requests = StudentEnrollmentRequest.objects.filter(
            user=user,
            generation__start_date__lte=end,
            generation__end_date__gte=start,
        )

        if overlapping_requests.exists():
            raise serializers.ValidationError("해당 기간에 겹치는 다른 과정의 신청 이력이 존재합니다.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        generation = validated_data["generation"]
        return StudentEnrollmentRequest.objects.create(user=user, generation=generation)
