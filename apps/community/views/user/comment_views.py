from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Comment, Post
from apps.community.serializers.comment_serializer import (
    CommentCreateSerializer,
    CommentResponseSerializer,
    CommentTagSerializer,
    CommentUpdateSerializer,
)

mock_existing_ids = range(1, 4)
unauthorized_ids = [99]


# 댓글 조희
class CommentListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="댓글 조회",
        summary="특정 게시글의 댓글 목록 조회",
        description="게시글 ID를 기반으로 해당 게시글에 달린 댓글 목록을 조회. 페이지네이션이 적용.",
        tags=["댓글"],
        responses={
            200: CommentResponseSerializer(many=True),
            400: OpenApiResponse(
                response={"detail": "post_id는 필수 항목입니다."}, description="post_id가 누락된 경우"
            ),
        },
        examples=[
            OpenApiExample(
                name="댓글 예시 응답",
                summary="댓글 목록 응답 예시",
                description="댓글 목록을 반환했을 때의 예시입니다.",
                value=[
                    {
                        "id": 1,
                        "content": "첫 번째 댓글.",
                        "author": {"id": 5, "nickname": "유저1"},
                        "tagged_users": [{"tagged_user": {"id": 6, "nickname": "유저2"}}],
                    },
                    {"id": 2, "content": "두 번째 댓글.", "author": {"id": 6, "nickname": "유저2"}, "tagged_users": []},
                ],
            )
        ],
    )
    def get(self, request: Request, post_id: int) -> Response:

        if not post_id:
            return Response({"detail": "post_id는 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not Post.objects.filter(id=post_id).exists():
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post_id=post_id).order_by("-created_at")

        if not comments.exists():
            return Response({"detail": "댓글이 없습니다."}, status=status.HTTP_200_OK)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_comments = paginator.paginate_queryset(comments, request)

        if paginated_comments is None:
            return paginator.get_paginated_response([])

        results = []
        for comment in paginated_comments:
            comment_data = CommentResponseSerializer(comment).data
            tag_data = CommentTagSerializer(comment.tags.all(), many=True).data
            comment_data["tagged_users"] = tag_data
            results.append(comment_data)

        return paginator.get_paginated_response(results)

        # if not post_id:
        #     return Response({"detail": "post_id는 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)
        # user1 = User(id=5, nickname="유저1")
        # user2 = User(id=6, nickname="유저2")
        #
        # post = Post(id=post_id)
        # mock_comment1 = Comment(
        #     id=1, post=post, author=user1, content="@tae 좋은 글 감사합니다!", created_at=datetime(2025, 6, 20, 13, 15)
        # )
        #
        # mock_comment2 = Comment(
        #     id=2, post=post, author=user2, content="동의합니다.", created_at=datetime(2025, 6, 20, 13, 16)
        # )
        # results = CommentResponseSerializer([mock_comment1, mock_comment2], many=True).data
        #
        # return Response(
        #     {"count": 23, "next": f"/api/v1/comments/?post_id={post_id}&page=2", "previous": None, "results": results},
        #     status=status.HTTP_200_OK,
        # )


class CommentCreateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="댓글 작성",
        summary="댓글 작성",
        description="게시글에 댓글을 작성합니다.",
        request=CommentCreateSerializer,
        responses={
            201: {"id": 45, "post_id": 123, "user": {"id": 7, "nickname": "태연123"}, "content": "입력한 댓글 내용"},
            400: {"detail": "내용이 비어 있습니다."},
        },
        tags=["댓글"],
    )
    def post(self, request: Request, post_id: int) -> Response:
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # mock_response = {
        #     "id": 45,
        #     "post_id": post_id,
        #     "user": {"id": 7, "nickname": "태연123"},
        #     "content": serializer.validated_data["content"],
        # }

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        comment = serializer.save(post=post)

        response_serializer = CommentResponseSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="댓글 수정",
        summary="댓글 수정",
        description="댓글 내용을 수정합니다.",
        tags=["댓글"],
        request=CommentUpdateSerializer,
        responses={
            200: CommentResponseSerializer,
            400: OpenApiResponse(description="변경할 내용이 없습니다."),
            403: OpenApiResponse(description="해당 댓글을 수정할 권한이 없습니다."),
        },
    )
    def patch(self, request: Request, comment_id: int) -> Response:

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        response_serializer = CommentResponseSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

        # mock_response = {
        #     "id": comment_id,
        #     "post_id": 45,
        #     "user": {"id": 7, "nickname": "정아"},
        #     "content": content,
        #     "updated_at": "2025-06-20T14:05:00Z",
        # }


class CommentDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="댓글 삭제",
        summary="댓글 삭제",
        description="댓글을 삭제합니다.",
        tags=["댓글"],
        responses={
            200: OpenApiResponse(description="댓글이 삭제되었습니다."),
            403: OpenApiResponse(description="해당 댓글을 삭제할 권한이 없습니다."),
            404: OpenApiResponse(description="존재하지 않는 댓글입니다."),
        },
    )
    def delete(self, request: Request, comment_id: int) -> Response:

        if comment_id not in mock_existing_ids:
            return Response({"detail": "해당 댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        if comment_id in unauthorized_ids:
            return Response({"detail": "해당 댓글을 삭제할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": "댓글이 삭제 되었습니다."}, status=status.HTTP_200_OK)
