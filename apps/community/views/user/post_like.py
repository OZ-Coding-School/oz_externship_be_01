from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post, PostLike
from apps.community.serializers.post_like_serializer import PostLikeResponseSerializer


class PostLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["게시글좋아요"],
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
            like.save()

        post.likes_count = PostLike.objects.filter(post=post, is_liked=True).count()
        post.save(update_fields=["likes_count"])

        return Response({"liked": True, "like_count": post.likes_count}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["게시글좋아요"],
        summary="게시글 좋아요 취소",
        description="로그인한 사용자가 게시글에 남긴 좋아요를 취소합니다.",
        responses={
            200: OpenApiResponse(PostLikeResponseSerializer),
            400: OpenApiResponse(description="좋아요한 내역이 없습니다."),
            401: OpenApiResponse(description="로그인 필요"),
            404: OpenApiResponse(description="존재하지 않는 게시글"),
        },
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "존재하지 않는 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            like = PostLike.objects.get(user=request.user, post=post)
        except PostLike.DoesNotExist:
            return Response({"detail": "좋아요한 내역이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if like.is_liked:
            like.is_liked = False
            like.save()

        post.likes_count = PostLike.objects.filter(post=post, is_liked=True).count()
        post.save(update_fields=["likes_count"])

        return Response({"liked": False, "like_count": post.likes_count}, status=status.HTTP_200_OK)
