from types import SimpleNamespace
from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import PostAttachment, PostImage
from apps.community.serializers.notice_serializers import (
    NoticeCreateSerializer,
    NoticeResponseSerializer,
)
from apps.tests.permissions import IsAdminOrStaff
from core.utils.s3_file_upload import S3Uploader


# 공지 사항 등록
class NoticeCreateAPIView(APIView):
    permission_classes = [IsAdminOrStaff]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=NoticeCreateSerializer,
        responses={201: NoticeResponseSerializer},
        summary="공지사항 등록",
        description="공지사항을 등록합니다. 저장되진 않으며 Swagger 문서 확인용입니다.",
        tags=["Admin - 커뮤니티 공지사항"],
    )
    def post(self, request: Request) -> Response:
        serializer = NoticeCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            uploader = S3Uploader()

            # 첨부파일 S3 업로드
            for file in request.FILES.getlist("attachments"):
                s3_key = f"attachments/{file.name}"
                url = uploader.upload_file(file, s3_key)
                if url:
                    PostAttachment.objects.create(post=post, file_url=url, file_name=file.name)

            # 이미지 S3 업로드
            for image in request.FILES.getlist("images"):
                s3_key = f"images/{image.name}"
                url = uploader.upload_file(image, s3_key)
                if url:
                    PostImage.objects.create(post=post, image_url=url, image_name=image.name)

            return Response(NoticeResponseSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
