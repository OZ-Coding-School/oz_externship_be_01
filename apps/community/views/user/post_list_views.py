from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_list_serializers import PostListViewSerializer


class PostListAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="게시글 목록 조회 '",
        description="게시글 목록을 정렬 조건과 함께 페이징하여 조회합니다.",
        tags=["community - 게시글"],
        parameters=[
            OpenApiParameter(
                name="ordering", description="정렬 기준 (recent, old, views, likes)", required=False, type=str
            ),
            OpenApiParameter(
                name="search_type",
                description="검색 타입 (title, content, author, title_content)",
                required=False,
                type=str,
            ),
            OpenApiParameter(name="keyword", description="검색 키워드", required=False, type=str),
            OpenApiParameter(name="category_id", type=int, description="카테고리 ID", required=False),
            OpenApiParameter(name="size", description="페이지당 항목 수", required=False, type=int),
            OpenApiParameter(name="page", description="페이지 번호", required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(description="게시글 목록 조회 성공"),
            400: OpenApiResponse(description="정렬 기준 유효성 실패"),
        },
    )
    def get(self, request: Request) -> Response:
        sort: str = request.query_params.get("ordering", "recent")
        valid_sort = {"recent": "-created_at", "old": "created_at", "views": "-view_count", "likes": "-likes_count"}

        if sort not in valid_sort:
            return Response(
                {
                    "error_code": "INVALID_QUERY",
                    "message": "요청한 정렬 기준이 유효하지 않습니다. 'recent','old', 'views', 'likes' 중 하나를 사용해 주세요.",
                },
                status=400,
            )
        queryset = Post.objects.filter(is_visible=True)

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

        # posts = Post.objects.filter(is_visible=True).order_by(valid_sort[sort])

        queryset = queryset.annotate(comment_total=Count("comments")).order_by(valid_sort[sort])

        paginator = PageNumberPagination()
        paginator.page_size_query_param = "size"
        paginated = paginator.paginate_queryset(queryset, request)

        serializer = PostListViewSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)
