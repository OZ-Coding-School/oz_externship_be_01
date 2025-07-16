from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post, PostLike
from apps.community.serializers.post_like_serializer import PostLikeResponseSerializer


class PostLikeTrueAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["[User] Community - Posts ( 게시글 )"],
        summary="게시글 좋아요 추가",
        description="로그인한 사용자가 게시글에 좋아요를 추가합니다.",
        responses={
            200: OpenApiResponse(PostLikeResponseSerializer),
            401: OpenApiResponse(description="로그인 필요"),
            404: OpenApiResponse(description="존재하지 않는 게시글"),
        },
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        like, _ = PostLike.objects.get_or_create(user=request.user, post=post)

        if not like.is_liked:
            like.is_liked = True
            like.save(update_fields=["is_liked"])

        likes_count = PostLike.objects.filter(post=post, is_liked=True).count()

        return Response({"liked": True, "likes_count": likes_count}, status=status.HTTP_200_OK)


class PostLikeFalseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["[User] Community - Posts ( 게시글 )"],
        summary="게시글 좋아요 취소",
        description="로그인한 사용자가 게시글에 눌러둔 좋아요를 취소합니다.",
        responses={
            200: OpenApiResponse(PostLikeResponseSerializer),
            400: OpenApiResponse(description="좋아요한 내역이 없습니다."),
            401: OpenApiResponse(description="로그인 필요"),
            404: OpenApiResponse(description="존재하지 않는 게시글"),
        },
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            like = PostLike.objects.get(user=request.user, post=post)
            if like.is_liked:
                like.is_liked = False
                like.save(update_fields=["is_liked"])
        except PostLike.DoesNotExist:
            pass

        likes_count = PostLike.objects.filter(post=post, is_liked=True).count()

        return Response({"liked": False, "likes_count": likes_count}, status=status.HTTP_200_OK)
