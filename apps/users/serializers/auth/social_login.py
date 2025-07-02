from rest_framework import serializers


class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(
        help_text="네이버에서 발급받은 access_token", error_messages={"required": "access_token은 필수입니다."}
    )
