from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.notice_serializers import (
    NoticeCreateSerializer,
    NoticeResponseSerializer,
)
from apps.tests.permissions import IsAdminOrStaff


# 공지 사항 등록
class NoticeCreateAPIView(APIView):
    permission_classes = [IsAdminOrStaff]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="admin_notice_create",
        request=NoticeCreateSerializer,
        responses=NoticeResponseSerializer,
        tags=["Admin Notice"],
    )
    def post(self, request: Request) -> Response:
        data = request.data.copy()

        if not data.get("attachments"):
            data.pop("attachments")
        if not data.get("images"):
            data.pop("images")

        serializer = NoticeCreateSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            post = serializer.save()

            post = Post.objects.prefetch_related("attachments", "images").get(id=post.id)
            return Response(NoticeResponseSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
