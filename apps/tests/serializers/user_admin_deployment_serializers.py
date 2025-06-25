from rest_framework import serializers

class CodeValidationRequestSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()
    access_code = serializers.CharField(max_length=64)


class DeploymentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    subject_name = serializers.CharField()
    course_turm = serializers.CharField()
    number_of_participants = serializers.IntegerField()
    average_score = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
