from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.community.serializers.notice_serializers import (
    NoticeCreateSerializer,
    NoticeResponseSerializer,
)


# 공지 사항 등록
class NoticeCreateAPIView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        serializer = NoticeCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            post = serializer.save()
            return Response(NoticeResponseSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
