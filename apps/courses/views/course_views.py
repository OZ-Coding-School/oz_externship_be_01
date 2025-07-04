from django.db.models import Count, Q
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser  # 관리자 권한 검사용

from apps.courses.models import Course, Generation
from apps.courses.serializers.course_serializers import (
    CourseListSerializer,
    CourseSerializer,
)
from apps.users.models.permissions import PermissionsStudent
from apps.users.models.student_enrollment import StudentEnrollmentRequest
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Admin - 과정 관리"],
    summary="과정 등록 및 목록 조회 API",
    description="관리자 또는 스태프 권한의 유저는 어드민 페이지 내에서 신규 과정을 등록 및 목록을 페이지네이션과 함께 조회할 수 있습니다.",
    auth=[{"BearerAuth": []}], # type: ignore
)

class CourseListCreateView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [IsAdminUser]  # 관리자 또는 스태프 권한 제한

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseSerializer  # POST 요청 시 등록용
        return CourseListSerializer  # GET 요청 시 목록용

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # annotate: generations_count, active_generations_count, total_students_count
        annotated = queryset.annotate(
            generations_count=Count("generations", distinct=True),
            active_generations_count=Count("generations", filter=~Q(generations__status="closed"), distinct=True),
            total_students_count=Count("generations__students", distinct=True),
        )

        page = self.paginate_queryset(annotated)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(annotated, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Admin - 과정 관리"],
    summary="등록된 과정 상세 조회,  등록된 과정 상세 수정 등록된 과정 삭제 API",
    description="관리자 또는 스태프 권한 사용자가 등록된 특정 과정의 상세 정보를 조회 및 특정 과정의 상세 정보를 수정 및 등록된 특정 과정을 삭제합니다.",
    auth=[{"BearerAuth": []}],  # type: ignore
)

class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]  # 관리자 또는 스태프 권한 제한

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        course = self.get_object()
        generations = Generation.objects.filter(course=course)

        for generation in generations:
            if PermissionsStudent.objects.filter(generation=generation).exists():
                raise ValidationError({"detail": f"{generation.number}기에 수강생이 등록되어 있어 삭제할 수 없습니다."})

            if StudentEnrollmentRequest.objects.filter(
                generation=generation, status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED
            ).exists():
                raise ValidationError({"detail": f"{generation.number}기에 승인된 수강생이 있어 삭제할 수 없습니다."})

        generations.delete()
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

