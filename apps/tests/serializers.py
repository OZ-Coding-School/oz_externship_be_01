# apps/tests/serializers.py

from rest_framework import serializers

class CodeValidationRequestSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField(
        help_text="배포 ID (예: 100, 999 등)"
    )
    access_code = serializers.CharField(
        max_length=100,
        help_text="참가용 액세스 코드"
    )
