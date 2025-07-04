from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post, PostAttachment, PostImage
from apps.community.serializers.post_pagination_serializers import (
    AdminPostPaginationSerializer,
)
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
            OpenApiParameter(name="category", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="is_visible", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY),
        ],
        tags=["Admin Post"],
    )
    def get(self, request: Request) -> Response:
        queryset = Post.objects.select_related("category", "author").all()

        # 필터링
        is_visible = request.query_params.get("is_visible")
        category_id = request.query_params.get("category_id")
        if is_visible is not None:
            queryset = queryset.filter(is_visible=is_visible.lower() == "true")
        if category_id and int(category_id) != 1:  # 1이면 전체보기
            queryset = queryset.filter(category_id=int(category_id))

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
            queryset = queryset.order_by("-is_notice", ordering)
        else:
            queryset = queryset.order_by("-is_notice", "-created_at")

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
            "results": PostListSerializer(list(page.object_list), many=True).data,
        }

        return Response(AdminPostPaginationSerializer(data).data)


# 어드민 게시글 상세 조회
class AdminPostDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_detail",
        request=None,
        responses=PostDetailSerializer,
        tags=["Admin Post"],
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
        tags=["Admin Post"],
    )
    def patch(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)
        serializer = PostUpdateSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            uploader = S3Uploader()

            # 파일 업로드 처리
            for file in request.FILES.getlist("attachments"):
                s3_key = f"oz_externship_be/community/attachments/{file.name}"
                url = uploader.upload_file(file, s3_key)
                if url:
                    PostAttachment.objects.create(post=post, file_url=url, file_name=file.name)

            for image in request.FILES.getlist("images"):
                s3_key = f"oz_externship_be/community/images/{image.name}"
                url = uploader.upload_file(image, s3_key)
                if url:
                    PostImage.objects.create(post=post, image_url=url, image_name=image.name)

            post = Post.objects.prefetch_related("attachments", "images").get(id=post.id)
            return Response(PostDetailSerializer(post).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 게시글 삭제
class AdminPostDeleteView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        operation_id="admin_post_delete",
        request=None,
        responses={"204": None},
        tags=["Admin Post"],
    )
    def delete(self, request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)
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
        tags=["Admin Post"],
    )
    def patch(self, request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)

        # 현재 값 반전
        post.is_visible = not post.is_visible
        post.save()

        return Response(
            {
                "message": f"게시글 노출 상태가 {'활성화' if post.is_visible else '비활성화'}되었습니다.",
                "data": PostDetailSerializer(post).data,
            },
            status=status.HTTP_200_OK,
        )
