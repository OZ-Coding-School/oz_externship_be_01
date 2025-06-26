from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.courses.serializers.course_serializers import (
    CourseListSerializer,
    CourseSerializer,
)


class CourseListCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="과정 목록 조회", responses=CourseListSerializer(many=True), tags=["course"])
    def get(self, request: Request) -> Response:
        mock_courses_data: list[dict[str, Any]] = [
            {
                "id": 1,
                "name": "AI 백엔드 심화과정",
                "tag": "AI1",
                "description": "AI 백엔드 개발 심화 교육과정입니다.",
                "thumbnail_img_url": "https://cdn.example.com/images/ai-course.png",
                "created_at": "2025-06-20T10:00:00Z",
                "updated_at": "2025-06-22T11:00:00Z",
            },
            {
                "id": 2,
                "name": "프론트엔드 기본 과정",
                "tag": "FE1",
                "description": "HTML, CSS, JS 기본기를 학습하는 과정",
                "thumbnail_img_url": "https://cdn.example.com/images/fe-course.png",
                "created_at": "2025-06-21T09:00:00Z",
                "updated_at": None,
            },
        ]

        mock_courses: list[Course] = [Course(**data) for data in mock_courses_data]

        serializer = CourseListSerializer(instance=mock_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="과정 등록", request=CourseSerializer, responses=CourseSerializer, tags=["course"])
    def post(self, request: Request) -> Response:
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            mock_response: dict[str, Any] = serializer.data.copy()
            mock_response["id"] = 1
            mock_response["created_at"] = "2025-06-23T14:31:00Z"
            mock_response["updated_at"] = None
            return Response(mock_response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="과정 상세 조회", responses=CourseSerializer, tags=["course"])
    def get(self, request: Request, course_id: int) -> Response:
        mock_course: dict[str, Any] = {
            "id": course_id,
            "name": "AI 백엔드 심화과정",
            "tag": "AI1",
            "description": "AI 백엔드 개발 심화 교육과정입니다.",
            "thumbnail_img_url": "https://cdn.example.com/images/ai-course.png",
            "created_at": "2025-06-20T10:00:00Z",
            "updated_at": "2025-06-23T14:31:00Z",
        }
        serializer = CourseSerializer(data=mock_course)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="과정 수정", request=CourseSerializer, responses=CourseSerializer, tags=["course"])
    def patch(self, request: Request, course_id: int) -> Response:
        serializer = CourseSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            mock_response: dict[str, Any] = {
                "id": course_id,
                "name": serializer.validated_data.get("name", "AI 백엔드 심화과정 v2"),
                "tag": "AI1",
                "description": serializer.validated_data.get("description", "최신 트렌드 반영된 AI 백엔드 과정"),
                "thumbnail_img_url": serializer.validated_data.get(
                    "thumbnail_img_url", "https://cdn.example.com/images/ai-course-v2.png"
                ),
                "created_at": "2025-06-20T10:00:00Z",
                "updated_at": "2025-06-23T15:12:22Z",
            }
            return Response(mock_response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="과정 삭제", responses={200: CourseSerializer}, tags=["course"])
    def delete(self, request: Request, course_id: int) -> Response:
        return Response({"detail": f"{course_id}번 과정이 삭제되었습니다."}, status=status.HTTP_200_OK)
