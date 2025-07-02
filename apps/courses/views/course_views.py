from typing import Any
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from apps.courses.models import Course, Generation
from apps.courses.serializers.course_serializers import (
    CourseListSerializer,
    CourseSerializer,
    CourseEnrollmentStatsSerializer,
    CourseEnrollmentListSerializer,
    EnrollmentRequestSerializer,
)
from apps.users.models.student_enrollment import StudentEnrollmentRequest
from apps.users.permissions import IsAdminOrStaff


class CourseListCreateView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = CourseAdminListSerializer
    pagination_class = PageNumberPagination

    @extend_schema(summary="과정 목록 조회", tags=["course"])
    def get(self, request: Request) -> Response:
        queryset = Course.objects.prefetch_related("generation_set").all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(summary="과정 등록", request=CourseSerializer, responses=CourseSerializer, tags=["course"])
    def post(self, request: Request) -> Response:
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    @extend_schema(summary="과정 상세 조회", responses=CourseSerializer, tags=["course"])
    def get(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, id=course_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="과정 수정", request=CourseSerializer, responses=CourseSerializer, tags=["course"])
    def patch(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, id=course_id)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            updated_course = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="과정 삭제", tags=["course"])
    def delete(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, id=course_id)
        generations = Generation.objects.filter(course=course)

        for generation in generations:
            if StudentEnrollmentRequest.objects.filter(generation=generation).exists():
                return Response(
                    {"detail": "해당 과정에 등록된 수강생이 있어 삭제할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        generations.delete()
        course.delete()
        return Response({"detail": f"{course_id}번 과정이 삭제되었습니다."}, status=status.HTTP_200_OK)


class CourseEnrollmentStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    @extend_schema(summary="과정별 수강 등록 통계 조회", responses=CourseEnrollmentStatsSerializer, tags=["course"])
    def get(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, id=course_id)
        enrollments = StudentEnrollmentRequest.objects.filter(generation__course_id=course_id).select_related(
            "generation", "user"
        )

        total_enrollments = enrollments.count()
        pending_enrollments = enrollments.filter(status="PENDING").count()
        approved_enrollments = enrollments.filter(status="APPROVED").count()
        rejected_enrollments = enrollments.filter(status="REJECTED").count()

        generation_stats = (
            enrollments.values("generation__id", "generation__number")
            .annotate(enrollment_count=Count("id"))
            .order_by("generation__number")
        )

        generations = []
        for stat in generation_stats:
            generation_obj = Generation.objects.filter(id=stat["generation__id"]).first()
            generations.append(
                {
                    "generation_id": stat["generation__id"],
                    "generation_number": stat["generation__number"],
                    "enrollment_count": stat["enrollment_count"],
                    "max_student": generation_obj.max_student if generation_obj else 0,
                    "status": generation_obj.status if generation_obj else "unknown",
                }
            )

        stats_data = {
            "course_id": course.id,
            "course_name": course.name,
            "total_enrollments": total_enrollments,
            "pending_enrollments": pending_enrollments,
            "approved_enrollments": approved_enrollments,
            "rejected_enrollments": rejected_enrollments,
            "generations": generations,
        }

        serializer = CourseEnrollmentStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnrollmentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    @extend_schema(summary="과정별 수강 등록 목록 조회", responses=CourseEnrollmentListSerializer, tags=["course"])
    def get(self, request: Request, course_id: int) -> Response:
        course = get_object_or_404(Course, id=course_id)
        enrollments = (
            StudentEnrollmentRequest.objects.filter(generation__course_id=course_id)
            .select_related("generation", "user")
            .order_by("-created_at")
        )

        enrollment_data = {"course_id": course.id, "course_name": course.name, "enrollments": enrollments}

        serializer = CourseEnrollmentListSerializer(data=enrollment_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
