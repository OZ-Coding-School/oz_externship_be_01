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


# 요청용 시리얼라이저
class CategoryStatusUpdateRequestSerializer(serializers.Serializer):
    status = serializers.BooleanField()


# 응답용 시리얼라이저
class CategoryStatusUpdateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    updated_at = serializers.DateTimeField()


# 카테고리 목록 조회 응답 시리얼라이저
class CategoryListResponseSerializer(ModelSerializer[PostCategory]):
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]


# 카테고리 이름 변경 요청 시리얼라이저
class CategoryRenameRequestSerializer(serializers.Serializer):
    name = serializers.CharField()


# 카테고리 이름 변경 응답 시리얼라이저
class CategoryRenameResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.BooleanField()
    updated_at = serializers.DateTimeField()
