from typing import Any, Dict

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.community.models import PostCategory


# 카테고리 상세 조회 응답 시리얼라이저
class CategoryDetailResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status"]


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


# 카테고리 on/off 상태변경 요청 시리얼라이저
class CategoryStatusUpdateRequestSerializer(ModelSerializer[PostCategory]):
    category_id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()


# 카테고리 on/off 상태변경 응답 시리얼라이저
class CategoryStatusUpdateResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["name", "status"]


# 카테고리 목록 조회 응답 시리얼라이저
class CategoryListResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]


# 카테고리 수정 응답 시리얼라이저
class CategoryUpdateResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "updated_at"]
