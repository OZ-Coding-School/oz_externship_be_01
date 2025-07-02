from typing import List

from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce, TruncMonth
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course, EnrollmentRequest, Generation
from apps.courses.serializers.generation_serializer import (
    CourseTrendSerializer,
    GenerationCreateSerializer,
    GenerationDetailSerializer,
    GenerationListSerializer,
    MonthlyCourseSerializer,
)
from apps.users.models.student_enrollment import StudentEnrollmentRequest


# 기수 등록 API
class GenerationCreateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationCreateSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 기수 목록 API
class GenerationListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationListSerializer

    def get(self, request: Request) -> Response:
        queryset = Generation.objects.select_related("course").annotate(registered_students=Count("students"))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 기수 상세 정보 API
class GenerationDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationListSerializer

    def get(self, request: Request, pk: int) -> Response:
        try:
            gen = Generation.objects.select_related("course").annotate(registered_students=Count("students")).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerationUpdateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationCreateSerializer

    def patch(self, request: Request, pk: int) -> Response:
        try:
            gen = Generation.objects.get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(gen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(GenerationDetailSerializer(gen).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerationDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request: Request, pk: int) -> Response:
        try:
            gen = Generation.objects.annotate(registered_students=Coalesce(Count("students"), 0)).get(pk=pk)
        except Generation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not gen.registered_students == 0 or None:
            return Response({"이미 등록된 학생이 있어 삭제할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

        gen.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseTrendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CourseTrendSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="조회할 과정의 ID",
                required=True,
            )
        ]
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        course_id = request.query_params.get("course_id")
        if not course_id:
            return Response(
                {"detail": "과정 ID(course_id)는 필수 쿼리 파라미터입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)

            # accepted_at이 NULL이 아닌 등록 요청만 카운트
            generations_data = (
                Generation.objects.filter(course=course)
                .annotate(
                    registered_students=Coalesce(
                        Count("enrollment_requests", filter=Q(enrollments_requests__accepted_at__isnull=False)), 0
                    )
                )
                .order_by("number")
            )

            labels: List[str | None] = []
            registered_students_count: List[int | None] = []

            for gen in generations_data:
                labels.append(f"{gen.number}기")
                registered_students_count.append(gen.registered_students)

            output_payload = {
                "course_id": course.id,
                "course_name": course.name,
                "labels": labels,
                "registered_students_count": registered_students_count,
            }

            serializer = self.serializer_class(output_payload)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"detail": "해당 과정을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"서버 오류: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MonthlyCourseView(APIView):
    permission_classes = [AllowAny]
    serializer_class = MonthlyCourseSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="조회할 과정 ID",
                required=True,
            )
        ]
    )
    def get(self, request: Request) -> Response:
        course_id = request.query_params.get("course_id")

        if not course_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(id=course_id)

            monthly_enrollments = (
                StudentEnrollmentRequest.objects.filter(
                    generation__course=course,  # 해당 과정에 속한 기수의 요청
                    accepted_at__isnull=False,  # 승인된 요청
                )
                .annotate(month_start=TruncMonth("accepted_at"))  # accepted_at을 월 단위로
                .values("month_start")
                .annotate(count=Count("id"))  # 해당 월 등록 요청 카운트
                .order_by("month_start")
            )  # 월별로 정렬

            labels: List[str] = []  # 데이터 가공
            monthly_enrollments_count: List[int] = []
            for entry in monthly_enrollments:
                labels.append(entry["month_start"].strftime("%Y-%m"))
                monthly_enrollments_count.append(entry["count"])

            payload = {
                "course_id": course.id,
                "course_name": course.name,
                "labels": labels,
                "monthly_enrollments_count": monthly_enrollments_count,
            }

            serializer = self.serializer_class(payload)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"detail": "해당 과정을 찾을 수 없습니다. "}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": f"서버오류: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class OngoingCourseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        # 활성화된 Generation을 select_related로 Course와 함께 가져옴 ( N + 1 문제 해결 )
        active_generations = Generation.objects.select_related("course").filter(~Q(status="closed"))

        if not active_generations.exists():
            return Response(
                data={"detail": "활성화된 과정-기수가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        # Generation ID와 연결된 Course 정보 추출
        generation_ids = [gen.id for gen in active_generations]
        course_id_name_map = {gen.course.id: gen.course.name for gen in active_generations}

        # 활성 Generation에 속한 승인된 수강신청 수를 Course별로 집계
        enrollment_counts = (
            StudentEnrollmentRequest.objects.filter(
                generation_id__in=generation_ids,
                status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED,
                accepted_at__isnull=False,
            )
            .values("generation__course__id")
            .annotate(count=Count("id"))
        )

        # Course 이름을 기준으로 응답 생성
        result = {}
        for row in enrollment_counts:
            course_id = row["generation__course__id"]
            course_name = course_id_name_map.get(course_id, "Unknown")
            result[course_name] = row["count"]

        return Response(result, status=status.HTTP_200_OK)
