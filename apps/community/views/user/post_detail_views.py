from typing import Any

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Comment, CommentTags, Post, PostLike
from apps.community.serializers.post_like_serializer import PostLikeResponseSerializer
from apps.community.serializers.post_serializers import PostDetailSerializer


class UserPostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="게시글 상세 조회 (기능구현 완료)",
        tags=["[User] Community - Posts ( 게시글 )"],
        responses=PostDetailSerializer,
        examples=[
            OpenApiExample(
                name="PostDetail Example",
                value={
                    "id": 101,
                    "category": {"id": 1, "name": "공지사항"},
                    "author": {"id": 1, "nickname": "zizon_seongwon"},
                    "title": "백엔드가 재밌나요?",
                    "content": "백엔드의 재미...",
                    "view_count": 100,
                    "likes_count": 10,
                    "comment_count": 5,
                    "is_visible": True,
                    "is_notice": False,
                    "attachments": [{"id": 1, "file_url": "https://example.com/file.pdf"}],
                    "images": [{"image_url": "https://example.com/image1.png"}],
                    "comments": [
                        {
                            "id": 1,
                            "author": {"id": 2, "nickname": "user123"},
                            "content": "좋은 글 감사합니다!",
                            "created_at": "2025-07-11T11:30:00Z",
                            "updated_at": "2025-07-11T11:30:00Z",
                            "tags": [{"tagged_user": {"id": 3, "nickname": "taguser1"}}],
                            "tagged_user_nicknames": ["taguser1"],
                        }
                    ],
                    "created_at": "2025-07-11T10:00:00Z",
                    "updated_at": "2025-07-11T11:00:00Z",
                },
                description="게시글 상세 조회 예시",
            )
        ],
    )
    def get(self, request: Request, post_id: int) -> Response:
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        is_liked = False
        if request.user.is_authenticated:
            is_liked = PostLike.objects.filter(post=post, user=request.user, is_liked=True).exists()

        like_data = PostLikeResponseSerializer({"liked": is_liked}).data

        serializer = PostDetailSerializer(post, context={"request": request})
        data = dict(serializer.data)

        data.pop("is_visible", None)
        data.pop("is_notice", None)

        for comment_dict in data.get("comments", []):
            comment_id = comment_dict["id"]

            tags = CommentTags.objects.select_related("tagged_user").filter(comment_id=comment_id)

            tagged_nicks = [
                tag.tagged_user.nickname for tag in tags if tag.tagged_user and hasattr(tag.tagged_user, "nickname")
            ]

            comment_dict["tagged_user_nicknames"] = tagged_nicks

        data.update(like_data)

        return Response(data, status=status.HTTP_200_OK)
