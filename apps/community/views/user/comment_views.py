import re

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Comment, CommentTags, Post
from apps.community.serializers.comment_serializers import (
    CommentCreateSerializer,
    CommentResponseSerializer,
    CommentUpdateSerializer,
)

User = get_user_model()


# 댓글 조희
class CommentListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="댓글 조회",
        summary="특정 게시글의 댓글 목록 조회 (기능구현 완료)",
        description="게시글 ID를 기반으로 해당 게시글에 달린 댓글 목록을 조회. 페이지네이션이 적용.",
        tags=["[User] Community - Comment ( 댓글 조회/생성/삭제/수정 )"],
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
            results.append(comment_data)

        return paginator.get_paginated_response(results)


class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="댓글 작성",
        summary="댓글 작성 (기능구현 완료)",
        description="게시글에 댓글을 작성합니다.",
        request=CommentCreateSerializer,
        responses={
            201: {"id": 45, "post_id": 123, "user": {"id": 7, "nickname": "태연123"}, "content": "입력한 댓글 내용"},
            400: {"detail": "내용이 비어 있습니다."},
        },
        tags=["[User] Community - Comment ( 댓글 조회/생성/삭제/수정 )"],
    )
    def post(self, request: Request, post_id: int) -> Response:
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # post_id = request.data.get("post_id")
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        comment = serializer.save(post=post, author=request.user)

        content = serializer.validated_data.get("content", "")
        tag_nicknames = re.findall(r"@(\w+)", content)

        for nickname in tag_nicknames:
            try:
                tagged_user = User.objects.get(nickname=nickname)
                CommentTags.objects.create(comment=comment, tagged_user=tagged_user)
            except User.DoesNotExist:
                continue

        response_serializer = CommentResponseSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="댓글 수정",
        summary="댓글 수정 (기능구현 완료)",
        description="댓글 내용을 수정합니다.",
        tags=["[User] Community - Comment ( 댓글 조회/생성/삭제/수정 )"],
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

        if comment.author != request.user:
            return Response({"detail": "해당 댓글을 수정할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        response_serializer = CommentResponseSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="댓글 삭제",
        summary="댓글 삭제 (기능구현 완료)",
        description="댓글을 삭제합니다.",
        tags=["[User] Community - Comment ( 댓글 조회/생성/삭제/수정 )"],
        responses={
            200: OpenApiResponse(description="댓글이 삭제되었습니다."),
            403: OpenApiResponse(description="해당 댓글을 삭제할 권한이 없습니다."),
            404: OpenApiResponse(description="존재하지 않는 댓글입니다."),
        },
    )
    def delete(self, request: Request, comment_id: int) -> Response:

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "존재하지 않는 댓글입니다."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response({"detail": "해당 댓글을 삭제할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"detail": "댓글이 삭제 되었습니다."}, status=status.HTTP_204_NO_CONTENT)
