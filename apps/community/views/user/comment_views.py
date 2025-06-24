from urllib.parse import urlencode

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


# 댓글 조희
class CommentListAPIView(APIView):
    def get(self, request: Request) -> Response:
        post_id = request.query_params.get("post_id")
        page = int(request.query_params.get("page", 1))

        if not post_id:
            return Response({"detail": "post_id는 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)

        results = [
            {
                "id": 1,
                "user": {"id": 5, "nickname": "coolguy"},
                "content": "@tae 좋은 글 감사합니다!",
                "created_at": "2025-06-20T13:15:00Z",
            },
            {
                "id": 2,
                "user": {"id": 6, "nickname": "연태"},
                "content": "동의합니다.",
                "created_at": "2025-06-20T13:16:00Z",
            },
        ]

        mock_response = {
            "count": 23,
            "next": f"/api/v1/comments/?{urlencode({'post_id': post_id, 'page': page + 1})}" if page == 1 else None,
            "previous": None if page == 1 else f"/api/v1/comments/?{urlencode({'post_id': post_id, 'page': page - 1})}",
            "results": results,
        }

        return Response(mock_response, status=status.HTTP_200_OK)


# 댓글 작성
class CommentCreateAPIView(APIView):
    def post(self, request: Request) -> Response:
        content = request.data.get("content")
        if not content:
            return Response({"detail": "내용이 비어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        mock_response = {
            "id": 45,
            "post_id": 123,
            "user": {"id": 7, "nickname": "태연123"},
            "content": content,
        }
        return Response(mock_response, status=status.HTTP_201_CREATED)


# 댓글 수정
class CommentUpdateAPIView(APIView):
    def patch(self, request: Request, comment_id: int) -> Response:
        content = request.data.get("content")

        if comment_id == 99:
            return Response({"detail": "해당 댓글을 수정할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        if not content:
            return Response({"detail": "변경할 내용이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        mock_response = {
            "id": comment_id,
            "post_id": 45,
            "user": {"id": 7, "nickname": "정아"},
            "content": content,
            "updated_at": "2025-06-20T14:05:00Z",
        }

        return Response(mock_response, status=status.HTTP_200_OK)
