from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.models import Post
from apps.community.serializers.post_create_serializers import PostCreateSerializer
from apps.community.serializers.post_serializers import PostDetailSerializer

User = get_user_model()


class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            201: OpenApiResponse(description="게시글 등록되었습니다."),
            400: OpenApiResponse(description="입력값 유효하지 않습니다."),
        },
        tags=["[User] Community - Posts ( 게시글 )"],
        summary="게시글 등록 (기능구현 완료)",
        description="게시글 제목, 내용, 카테고리, 이미지를 생성한 예시입니다.",
    )
    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response(
                {
                    "detail": "필수 필드가 누락되었습니다.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response({"detail": "게시글이 성공적으로 등록되었습니다."}, status=status.HTTP_201_CREATED)
