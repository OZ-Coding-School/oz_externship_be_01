from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema  # 누락 방지용
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import Course, Generation
from apps.courses.serializers.course_serializers import (
    CourseListSerializer,
    CourseSerializer,
)
from apps.users.models import User
from apps.users.models.permissions import PermissionsStudent
from apps.users.models.student_enrollment import StudentEnrollmentRequest


# 임시 직접 정의한 권한 클래스 (mypy 오류)
class IsAdminOrStaff(BasePermission):
    message = "관리자 또는 스태프 권한이 필요합니다."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        excluded_roles = {User.Role.GENERAL, User.Role.STUDENT}
        allowed_roles = [role for role, _ in User.Role.choices if role not in excluded_roles]
        return user.role in allowed_roles


@extend_schema(
    tags=["Admin - 과정관리"],
    description="어드민 페이지 단의 과정 생성, 목록 조회 API입니다",
)
class CourseListCreateView(ListCreateAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = CourseListSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseSerializer  # S3Uploader를 사용하는 CourseSerializer 반환
        return CourseListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().annotate(
            generations_count=Count("generations", distinct=True),
            active_generations_count=Count("generations", filter=~Q(generations__status="closed"), distinct=True),
            total_students_count=Count("generations__students", distinct=True),
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()  # S3Uploader로 썸네일 업로드 & thumbnail_img_url 저장됨
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Admin - 과정관리"],
    description="어드민 페이지 단의 과정 상세 조회, 수정, 삭제 API입니다",
)
class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer  # S3Uploader를 사용하는 시리얼라이저
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    lookup_url_kwarg = "course_id"

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # 썸네일 수정 시 S3Uploader로 재업로드 처리됨
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
