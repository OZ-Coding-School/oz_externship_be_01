from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.community.models import PostCategory


class CategoryDetailResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]


# 카테고리 생성 요청 시리얼라이저
class CategoryCreateRequestSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["name", "status"]


# 카테고리 생성 응답 시리얼라이저
class CategoryCreateResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]


class CategoryStatusUpdateResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["categoies_id", "name", "status"]


class CategoryListResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]


class CategoryUpdateRequestSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "updated_at"]
