from typing import Any, Dict

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.views.user.post_create_views import PostCreateSerializer

User = get_user_model()


class PostCreateAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            201: OpenApiResponse(description="게시글 등록되었습니다."),
            400: OpenApiResponse(description="입력값 유효하지 않습니다."),
        },
        tags=["게시글"],
        summary="게시글 등록",
        description="게시글 제목, 내용, 카테고리, 이미지를ㅅ 생성한 예시입니다.",
    )
    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "detail": "필수 필드가 누락되었습니다.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        # post = Post.objects.create(category=category, author=author, **validated_data)
        #
        # PostAttachment.objects.bulk_create([             # 1:n 관계
        #     PostAttachment(post=post, file=attachment) for attachment in attachments_data
        # ])
        #
        # PostImage.objects.bulk_create([
        #     PostImage(post=post, image=image) for image in images_data
        # ])
        return Response({"detail": "게시글 등록됨"}, status=status.HTTP_201_CREATED)
