from django.db.models import Count
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_serializers import PostListSerializer


class PostListAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="게시글 목록 조회",
        description="게시글 목록을 정렬 조건과 함께 페이징하여 조회합니다.",
        tags=["게시글"],
        responses={
            200: OpenApiResponse(description="게시글 목록 조회 성공"),
            400: OpenApiResponse(description="정렬 기준 유효성 실패"),
        },
    )
    def get(self, request: Request) -> Response:
        sort: str = request.query_params.get("sort", "latest")
        valid_sort = {"latest": "-created_at", "views": "-view_count", "likes": "-likes_count"}

        if sort not in valid_sort:
            return Response(
                {
                    "error_code": "INVALID_QUERY",
                    "message": "요청한 정렬 기준이 유효하지 않습니다. 'latest', 'views', 'likes' 중 하나를 사용해 주세요.",
                },
                status=400,
            )

        # posts = Post.objects.filter(is_visible=True).order_by(valid_sort[sort])

        posts = (
            Post.objects.filter(is_visible=True).annotate(comment_total=Count("comments")).order_by(valid_sort[sort])
        )

        results = []
        for post in posts:
            comment_count = post.comments.count()
            results.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "comment_count": comment_count,
                }
            )

        paginator = PageNumberPagination()
        paginated = paginator.paginate_queryset(posts, request)

        serializer = PostListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)
