from datetime import datetime

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import PostCategory
from apps.community.serializers.category_serializers import (
    CategoryCreateRequestSerializer,
    CategoryCreateResponseSerializer,
    CategoryDetailResponseSerializer,
    CategoryListResponseSerializer,
    CategoryRenameRequestSerializer,
    CategoryRenameResponseSerializer,
    CategoryStatusUpdateRequestSerializer,
    CategoryStatusUpdateResponseSerializer,
)
from apps.tests.permissions import IsAdminOrStaff
from apps.users.models.user import User


# 커뮤니티 게시판 카테고리 상세 조회 APIView
class AdminCommunityCategoryDetailAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="커뮤니티 게시판 카테고리 상세 조회",
        description="카테고리 ID로 커뮤니티 게시판 카테고리 상세정보를 조회합니다.",
        responses={200: CategoryDetailResponseSerializer, 404: CategoryDetailResponseSerializer},
    )
    def get(self, request: Request, category_id: int) -> Response:
        category = get_object_or_404(PostCategory, id=category_id)

        serializer = CategoryDetailResponseSerializer(instance=category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 카테고리 삭제 API뷰
    @extend_schema(
        tags=["[Admin-category]"],
        operation_id="admin_category_delete",
        summary="관리자 카테고리 삭제",
        description="존재하는 카테고리를 삭제합니다.",
    )
    def delete(self, request: Request, category_id: int) -> Response:
        category = get_object_or_404(PostCategory, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 카테고리 생성
class AdminCommunityCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="커뮤니티 게시판 카테고리 생성",
        description="새로운 커뮤니티 카테고리를 생성합니다.",
        request=CategoryCreateRequestSerializer,
        responses={201: CategoryCreateResponseSerializer, 400: CategoryCreateResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = CategoryCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "카테고리 이름은 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)
        category = serializer.save()
        rsp_serializer = CategoryCreateResponseSerializer(category)
        return Response(rsp_serializer.data, status=status.HTTP_201_CREATED)


# 카테고리 상태 ON API
class CategoryStatusOnAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리 상태 ON",
        request=CategoryStatusUpdateRequestSerializer,
        responses={200: CategoryStatusUpdateResponseSerializer, 400: CategoryStatusUpdateResponseSerializer},
    )
    def post(self, request, category_id: int) -> Response:
        serializer = CategoryStatusUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "요청이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(PostCategory, id=category_id)

        category.status = True
        category.save()

        response = CategoryStatusUpdateResponseSerializer(instance=category)
        return Response(response.data, status=status.HTTP_200_OK)


# 카테고리 상태 OFF API
class CategoryStatusOffAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리 상태 OFF",
        request=CategoryStatusUpdateRequestSerializer,
        responses={200: CategoryStatusUpdateResponseSerializer, 400: CategoryStatusUpdateResponseSerializer},
    )
    def post(self, request, category_id: int) -> Response:
        serializer = CategoryStatusUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "요청이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(PostCategory, id=category_id)

        category.status = False
        category.save()

        response = CategoryStatusUpdateResponseSerializer(instance=category)
        return Response(response.data, status=status.HTTP_200_OK)


# 카테고리 목록 조회
class AdminCategoryListAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리 목록 조회",
        description="카테고리 목록을 조회합니다.",
        responses={200: CategoryListResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        categories = PostCategory.objects.all().order_by("-created_at")
        if not categories:
            return Response({"detail": "등록된 카테고리가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryListResponseSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 커뮤니티 게시판 카테고리 수정
class AdminCategoryRenameAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-category]"],
        summary="카테고리명 수정",
        request=CategoryRenameRequestSerializer,
        responses={200: CategoryRenameResponseSerializer, 400: CategoryRenameResponseSerializer},
    )
    def patch(self, request: Request, category_id: int) -> Response:
        category = PostCategory.objects.get(id=category_id)

        serializer = CategoryRenameRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            return Response({"detail": "카테고리 이름은 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)

        category.name = serializer.validated_data["name"]
        category.save()

        response = CategoryRenameResponseSerializer(category)
        return Response(response.data, status=200)
