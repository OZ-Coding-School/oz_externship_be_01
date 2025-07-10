from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post


class PostDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["[User] Community - Posts ( 게시글 좋아요, 삭제)"],
        summary="게시글 삭제",
        description=(
            "로그인한 사용자가 자신의 게시글을 삭제합니다. "
            "관리자(staff)는 모든 게시글을 삭제할 수 있습니다."
        ),
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            403: OpenApiResponse(description="삭제 권한 없음"),
            404: OpenApiResponse(description="존재하지 않는 게시글"),
        },
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        # 작성자 본인 또는 관리자 권한 확인
        is_staff = getattr(request.user, "is_staff", False)
        if request.user != post.author and not is_staff:
            return Response({"detail": "게시글 삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
