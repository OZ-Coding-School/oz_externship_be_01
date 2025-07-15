from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_serializers import PostDetailSerializer
from apps.community.serializers.user_post_serializers import UserPostUpdateSerializer


class UserPostUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="user_post_update",
        request=UserPostUpdateSerializer,
        responses=PostDetailSerializer,
        tags=["[User] Community - Posts ( 게시글 )"],
        summary="사용자 게시글 수정( 기능 구현 )",
    )
    def patch(self, request: Request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)

        if post.author != request.user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserPostUpdateSerializer(post, data=request.data, context={"request": request}, partial=True)

        if serializer.is_valid():
            updated_post = serializer.save()
            updated_post = Post.objects.prefetch_related("attachments", "images").get(id=updated_post.id)
            return Response(PostDetailSerializer(updated_post).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
