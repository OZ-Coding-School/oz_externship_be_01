from django.db.models import F
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post, PostCategory
from apps.community.serializers.post_serializers import (
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
)
from apps.tests.permissions import IsAdminOrStaff
from core.utils.s3_file_upload import S3Uploader


# 어드민 게시글 목록 조회
class AdminPostListView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_list",
        request=None,
        responses=PostListSerializer,
        parameters=[
            OpenApiParameter(name="page", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="size", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="category_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="is_visible", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="search_type", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="검색 대상: 작성자 | 제목( 기본값 ) | 내용 | 제목 + 내용 "),
            OpenApiParameter(name="keyword", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="검색 키워드"),
            OpenApiParameter(name="ordering", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="정렬: 최신순( 기본값 ) | 오래된 순  | 조회수 많은 순 | 좋아요가 많은 순 "),
        ],
        tags=["[Admin] Community - Posts(게시글 목록조회, 상세조회, 수정, 삭제, 노출 on/off, 공지사항 등록"],
        summary="관리자 게시글 목록 조회 (기능 구현)",
    )
    def get(self, request: Request) -> Response:
        queryset = Post.objects.select_related("category", "author").all()

        # 필터링
        is_visible = request.query_params.get("is_visible")
        category_id = request.query_params.get("category_id")
        if is_visible is not None:
            queryset = queryset.filter(is_visible=is_visible.lower() == "true")
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except (ValueError, PostCategory.DoesNotExist):
                pass

        # 검색 필터링
        search_type = request.query_params.get("search_type") or "title"
        keyword = request.query_params.get("keyword")
        if keyword:
            if search_type == "title":
                queryset = queryset.filter(title__icontains=keyword)
            elif search_type == "content":
                queryset = queryset.filter(content__icontains=keyword)
            elif search_type == "author":
                queryset = queryset.filter(author__nickname__icontains=keyword)
            elif search_type == "title_content":
                queryset = queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
            else:
                queryset = queryset.filter(title__icontains=keyword)

            if not queryset.exists():
                return Response(
                    {"detail": {"code": "NOT_FOUND", "message": "검색 결과가 없습니다."}},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # 정렬 처리
        ordering_param = request.query_params.get("ordering", "recent")
        ordering_map = {
            "recent": "-created_at",
            "old": "created_at",
            "view": "-view_count",
            "like": "-likes_count",
        }

        # 정렬
        ordering = ordering_map.get(ordering_param)
        if ordering:
            queryset = queryset.order_by("-is_notice", ordering)
        else:
            queryset = queryset.order_by("-is_notice", "-created_at")

        # 페이지네이션
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "size"
        result_page = paginator.paginate_queryset(queryset, request)

        return paginator.get_paginated_response(PostListSerializer(result_page, many=True).data)


# 어드민 게시글 상세 조회
class AdminPostDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_detail",
        request=None,
        responses=PostDetailSerializer,
        tags=["[Admin] Community - Posts(게시글 목록조회, 상세조회, 수정, 삭제, 노출 on/off, 공지사항 등록"],
        summary="관리자 게시글 상세 조회(기능 구현)",
    )
    def get(self, request: Request, post_id: int) -> Response:

        post = get_object_or_404(
            Post.objects.select_related("category", "author").prefetch_related(
                "attachments",
                "images",
                "comments__author",
                "comments__tags__tagged_user",
            ),
            id=post_id,
        )
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)


# 어드민 게시글 수정
class AdminPostUpdateView(APIView):
    permission_classes = [IsAdminOrStaff]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="admin_post_update",
        request=PostUpdateSerializer,
        responses=PostDetailSerializer,
        tags=["[Admin] Community - Posts(게시글 목록조회, 상세조회, 수정, 삭제, 노출 on/off, 공지사항 등록"],
        summary="관리자 게시글 수정(기능 구현)",
    )
    def patch(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)

        serializer = PostUpdateSerializer(post, data=request.data, context={"request": request}, partial=True)

        if serializer.is_valid():
            updated_post = serializer.save()
            updated_post = Post.objects.prefetch_related("attachments", "images").get(id=updated_post.id)
            return Response(PostDetailSerializer(updated_post).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 게시글 삭제
class AdminPostDeleteView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_delete",
        request=None,
        responses={"204": None},
        tags=["[Admin] Community - Posts(게시글 목록조회, 상세조회, 수정, 삭제, 노출 on/off, 공지사항 등록"],
        summary="관리자 게시글 삭제(기능 구현)",
    )
    def delete(self, request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)
        uploader = S3Uploader()

        for attachment in post.attachments.all():
            uploader.delete_file(attachment.file_url)
        post.attachments.all().delete()


        for image in post.images.all():
            uploader.delete_file(image.image_url)
        post.images.all().delete()

        post.delete()
        return Response({"id": post_id, "message": "게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


# 게시글 노출 on/off
class AdminPostVisibilityToggleView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_visibility_toggle",
        request=None,
        responses={
            200: OpenApiResponse(
                description="게시글 노출 상태가 정상적으로 변경되었습니다.", response=PostDetailSerializer
            )
        },
        tags=["[Admin] Community - Posts(게시글 목록조회, 상세조회, 수정, 삭제, 노출 on/off, 공지사항 등록"],
        summary="관리자 게시글 노출 on/off(기능 구현)",
    )
    def patch(self, request, post_id: int) -> Response:
        with transaction.atomic():
            updated_count = Post.objects.filter(id=post_id).update(is_visible=~F("is_visible"))

            if updated_count == 0:
                return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        post = Post.objects.get(id=post_id)

        return Response(
            {
                "message": f"게시글 노출 상태가 {'활성화' if post.is_visible else '비활성화'}되었습니다.",
                "data": PostDetailSerializer(post).data,
            },
            status=status.HTTP_200_OK,
        )
