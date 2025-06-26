from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.community_serializer import (
    CommentDeleteResponseSerializer,
)

# 1, 2, 3번 댓글만 존재하는걸로 임의로 결정?
mock_existing_ids = [i for i in range(1, 4)]


class AdminCommentDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Admin"],
        operation_id="admin_comment_delete",
        summary="관리자 댓글 삭제",
        description="1, 2, 3번 댓글만 존재하는 것으로 간주하고 그 외 ID는 삭제 실패로 처리.",
        responses={200: CommentDeleteResponseSerializer, 404: CommentDeleteResponseSerializer},
    )
    def delete(self, request: Request, comment_id: int) -> Response:
        if comment_id not in mock_existing_ids:
            serializer = CommentDeleteResponseSerializer({"detail": "해당 댓글이 존재하지 않습니다."})
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentDeleteResponseSerializer({"detail": "댓글이 삭제되었습니다."})
        return Response(serializer.data, status=status.HTTP_200_OK)
