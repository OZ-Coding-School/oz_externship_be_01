from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView


# 공지사항 등록
class NoticeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = request.user

        # 관리자 권한 체크
        if getattr(user, "role", None) != "ADMIN":
            return Response({"detail": "관리자 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 요청 본문 필드 추출
        title = request.data.get("title")
        content = request.data.get("content")
        category_id = request.data.get("category_id")
        is_notice = request.data.get("is_notice")
        is_visible = request.data.get("is_visible", True)
        attachments = request.data.get("attachments", [])
        images = request.data.get("images", [])

        # 필수 항목 검증
        if not title or not content or not category_id or is_notice is not True:
            return Response({"detail": "제목과 내용은 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 성공 Mock 응답 반환
        return Response(
            {"message": "공지사항이 성공적으로 등록되었습니다.", "created_post_id": 1203},  # Mock ID
            status=status.HTTP_200_OK,
        )
