from types import SimpleNamespace
from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post, PostCategory
from apps.community.serializers.notice_serializers import (
    NoticeCreateSerializer,
    NoticeResponseSerializer,
)


# 공지 사항 등록
class NoticeCreateAPIView(APIView):
    permission_classes = [AllowAny]  # 실제 api 경우 IsAuthenticated

    @extend_schema(
        request=NoticeCreateSerializer,
        responses={201: NoticeResponseSerializer},
        summary="공지사항 등록",
        description="공지사항을 등록합니다. 저장되진 않으며 Swagger 문서 확인용입니다.",
        tags=["Admin - 커뮤니티 공지사항"],
    )
    def post(self, request: Request) -> Response:
        # 요청 데이터 유효성 검사
        serializer = NoticeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # category.name 동적 대응
        category_id = serializer.validated_data["category_id"]
        # 실제 DB 조회 생략 → category는 가상의 값
        mock_category = PostCategory(id=category_id, name=f"카테고리 {category_id}")

        # 가상으로 응답할 데이터 (실제 DB 저장은 생략)
        notice_post = {
            "id": 10,
            "title": serializer.validated_data["title"],
            "content": serializer.validated_data["content"],
            "is_notice": serializer.validated_data["is_notice"],
            "is_visible": serializer.validated_data.get("is_visible", True),
            "category": {
                "id": category_id,
                "name": mock_category.name,
            },
            "attachments": serializer.validated_data.get("attachments", []),
            "images": serializer.validated_data.get("images", []),
            "created_at": "2025-06-24T18:00:00Z",
            "updated_at": "2025-06-24T18:00:00Z",
        }

        mock_instance = cast(Post, SimpleNamespace(**notice_post))
        resp_serializer = NoticeResponseSerializer(instance=mock_instance)
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)
