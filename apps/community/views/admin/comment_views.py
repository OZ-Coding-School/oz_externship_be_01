from drf_spectacular.utils import extend_schema, OpenApi, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminOrStaff
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class AdminCommentDeleteAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["[Admin-comment]"],
        summary="댓글 삭제",
        description="댓글 ID를 기준으로 실제 댓글을 삭제합니다.",
        responses={
            204: OpenApiResponse(description="댓글이 삭제되었습니다."),
            404: OpenApiResponse(description="존재하지 않는 댓글입니다."),
        },
    )
    def delete(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)