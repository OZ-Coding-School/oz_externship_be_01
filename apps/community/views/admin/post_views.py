from types import SimpleNamespace
from typing import List, cast
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_pagination_serializers import (
    AdminPostPaginationSerializer,
)
from apps.community.serializers.post_serializers import (
    PostDetailSerializer,
    PostUpdateSerializer, PostListSerializer,
)

# 어드민 게시글 목록 조회
class AdminPostListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:
        queryset = Post.objects.select_related("category", "author").all()

        # 필터링
        is_visible = request.query_params.get("is_visible")
        category_id = request.query_params.get("category_id")
        if is_visible is not None:
            queryset = queryset.filter(is_visible=is_visible.lower() == "true")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 검색 필터링
        search_type = request.query_params.get("search_type")
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
            queryset = queryset.order_by(ordering)

        # 페이지네이션
        page_number = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("size", 10))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)

        base_url = request.build_absolute_uri(request.path)
        query_params = request.query_params.copy()

        def build_url(new_page: int) -> str:
            query_params["page"] = str(new_page)
            return f"{base_url}?{urlencode(query_params)}"

        next_url = build_url(page.next_page_number()) if page.has_next() else None
        prev_url = build_url(page.previous_page_number()) if page.has_previous() else None

        data = {
            "count": paginator.count,
            "next": next_url,
            "previous": prev_url,
            "results": PostListSerializer(page.object_list, many=True).data,
        }

        return Response(AdminPostPaginationSerializer(data).data)


# 어드민 게시글 상세 조회
class AdminPostDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request, post_id: int) -> Response:
        from django.shortcuts import get_object_or_404
        post = get_object_or_404(
            Post.objects.select_related("category", "author")
            .prefetch_related(
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
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)
        serializer = PostUpdateSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(PostDetailSerializer(post).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 게시글 삭제
class AdminPostDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="admin 게시글 삭제",
        description="관리자 페이지에서 게시글을 삭제하는 mock API입니다.",
        responses={
            200: OpenApiResponse(description="게시글이 삭제되었습니다."),
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=["Community - 게시글"],
    )
    def delete(self, request: Request, post_id: int) -> Response:
        global mock_post_cache
        _ = get_post_by_id(post_id)  # 없으면 Http404 발생

        mock_post_cache = [p for p in mock_post_cache if p.id != post_id]
        return Response({"detail": "게시글이 삭제되었습니다."}, status=200)


# 게시글 노출 on/off
class AdminPostVisibilityToggleView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="admin 게시글 노출 상태 토글",
        description="관리자 페이지에서 게시글의 노출 상태를 on/off로 변경하는 mock API입니다.",
        responses={
            200: OpenApiResponse(description="게시글 노출 상태가 변경되었습니다."),
            404: OpenApiResponse(description="존재하지 않는 게시글입니다."),
        },
        tags=["Community - 게시글"],
    )
    def patch(self, request: Request, post_id: int) -> Response:
        post = get_post_by_id(post_id)  # 없으면 Http404 발생

        new_is_visible = not post.is_visible
        post.is_visible = new_is_visible

        for idx, p in enumerate(mock_post_cache):
            if p.id == post_id:
                mock_post_cache[idx] = post
                break

        return Response(
            {
                "id": post.id,
                "is_visible": post.is_visible,
                "message": f"게시글 노출 상태가 {'ON' if post.is_visible else 'OFF'}으로 변경되었습니다.",
            },
            status=status.HTTP_200_OK,
        )
