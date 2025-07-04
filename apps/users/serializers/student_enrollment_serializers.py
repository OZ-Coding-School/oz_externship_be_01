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
        if StudentEnrollmentRequest.objects.filter(user=user, generation=generation).exists():
            raise serializers.ValidationError("이미 해당 기수에 신청한 이력이 있습니다.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        generation = validated_data["generation"]
        return StudentEnrollmentRequest.objects.create(user=user, generation=generation)
