from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.community.models import PostCategory
from apps.community.serializers.post_serializers import PostUpdateSerializer

User = get_user_model()


class UserPostUpdateSerializer(PostUpdateSerializer):
    class Meta(PostUpdateSerializer.Meta):
        fields = PostUpdateSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("is_visible", None)

    def validate_category_id(self, value):
        if not PostCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 카테고리입니다.")
        return value

    def validate_author_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        return value
