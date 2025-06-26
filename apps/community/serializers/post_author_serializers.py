from django.contrib.auth import get_user_model
from rest_framework import serializers


# 현재 프로젝트의 사용자 모델 (settings.AUTH_USER_MODEL) 동적 로드
User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer[User]):

    class Meta:
        model = User
        fields = (
            'id',
            'nickname',
            'profile_image_url',
        )

