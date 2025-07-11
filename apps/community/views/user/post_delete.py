from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from core.utils.s3_file_upload import S3Uploader


class PostDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="user_post_delete",
        tags=["[User] Community - Posts ( 게시글 )"],
        summary="유저가 자신의 게시물 삭제",
        request=None,
        responses={204: None},
    )
    def delete(self, request, post_id: int) -> Response:
        post = get_object_or_404(Post, id=post_id)

        # 작성자 본인만 삭제 가능
        if post.author != request.user:
            raise PermissionDenied("본인의 게시물만 삭제할 수 있습니다.")

        uploader = S3Uploader()

        for attachment in post.attachments.all():
            uploader.delete_file(attachment.file_url)
        post.attachments.all().delete()

        for image in post.images.all():
            uploader.delete_file(image.image_url)
        post.images.all().delete()

        post.delete()
        return Response({"id": post_id, "message": "게시물이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
