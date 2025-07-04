from django.db.models import Count, Q
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from apps.courses.models import Course, Generation
from apps.courses.serializers.course_serializers import (
    CourseListSerializer,
    CourseSerializer,
)
from apps.users.models.permissions import PermissionsStudent
from apps.users.models.student_enrollment import StudentEnrollmentRequest
from tests.views.permissions import IsAdminOrStaff  # 권한 클래스 교체


class CourseListCreateView(ListCreateAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAdminOrStaff]  # 리뷰 반영
    serializer_class = CourseListSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseSerializer
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
        course = serializer.save()
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrStaff]  # 리뷰 반영
    lookup_url_kwarg = "course_id"  # 리뷰 반영: path 파라미터 인식

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
                generation=generation,
                status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED
            ).exists():
                raise ValidationError({"detail": f"{generation.number}기에 승인된 수강생이 있어 삭제할 수 없습니다."})

        generations.delete()
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

