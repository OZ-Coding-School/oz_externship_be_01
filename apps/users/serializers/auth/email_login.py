from rest_framework import serializers

from apps.users.models import User


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class EmailLoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "phone_number",
            "gender",
            "birthday",
            "profile_image_url",
            "role",
        )
