from typing import List

from django.db import IntegrityError
from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce, TruncMonth
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.core.pagination import CustomPageNumberPagination
from apps.courses.models import Course, Generation
from apps.courses.serializers.generation_serializer import (
    CourseTrendSerializer,
    GenerationCreateSerializer,
    GenerationDetailSerializer,
    GenerationListSerializer,
    GenerationUpdateSerializer,
    MonthlyCourseSerializer,
)
from apps.tests.permissions import IsAdminOrStaff
from apps.users.models.permissions import PermissionsStudent
from apps.users.models.student_enrollment import StudentEnrollmentRequest


@extend_schema(
    tags=["Admin - 기수관리"],
    summary="기수등록 API",
)
# 기수 등록 API
class GenerationCreateView(APIView):
    permission_classes = [IsAuthenticated,IsAdminOrStaff]
    serializer_class = GenerationCreateSerializer

    @extend_schema(
        summary="신규 기수 등록",
        description="관리자 또는 스태프 권한이 있으면 새로운 기수를 등록할 수 있습니다.",
        request=GenerationCreateSerializer,
        responses={
            status.HTTP_201_CREATED: GenerationCreateSerializer,
            status.HTTP_400_BAD_REQUEST: {
                "description": "유효성 검증 실패 (Request Body 오류, 날짜 오류, 인원 오류 등)"
            },
            status.HTTP_401_UNAUTHORIZED: {"description": "인증 실패 (로그인 필요)"},
            status.HTTP_403_FORBIDDEN: {"description": "권한 부족 (관리자/스태프 아님)"},
            status.HTTP_404_NOT_FOUND: {"description": "과정을 찾을 수 없음 (제공된 course_id에 해당하는 과정 없음)"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "서버 내부 오류"},
        },
        examples=[
            OpenApiExample(
                "기수 등록 요청 성공 예시",
                value={
                    "course_id": 1,
                    "number": 1,
                    "max_student": 45,
                    "start_date": "2025-07-01",
                    "end_date": "2025-12-31",
                },
                request_only=True,
                media_type="application/json",
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        generation = serializer.save()

        return Response(self.serializer_class(generation).data, status=status.HTTP_201_CREATED)


# 기수 목록 API
@extend_schema(
    tags=["Admin - 기수관리"],
    summary="기수목록 API",
)
# apps/courses/views/generation_views.py


class GenerationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = GenerationListSerializer
    pagination_class = CustomPageNumberPagination

    @extend_schema(
        summary="등록된 기수 목록 조회",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="과정ID를 통해 특정 기수 조회",
                required=False,
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="조회할 페이지 번호",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="페이지당 항목 수 (default: 10, max: 100)",
                required=False,
            ),
        ],
    )
    def get_queryset(self):
        queryset = Generation.objects.annotate(
            registered_students=Coalesce(
                Count("enrollment_requests", filter=Q(enrollment_requests__accepted_at__isnull=False)), 0
            )
        ).select_related("course")

        queryset = queryset.order_by("course__name", "number")  # 이름 순으로 정렬 후 기수 순으로 정렬

        course_id = self.request.query_params.get("course_id")
        if course_id:
            try:
                queryset = queryset.filter(course__id=int(course_id))
            except ValueError:
                return Generation.objects.none()
        return queryset


# 기수 상세 정보 API
@extend_schema(
    tags=["Admin - 기수관리"],
    summary="기수상세정보 API",
)
class GenerationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = GenerationDetailSerializer
    lookup_field = "pk"

    @extend_schema(
        description="특정 기수의 상세정보 조회",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="조회할 기수의 고유 ID",
                required=True,
            )
        ],
        responses={
            status.HTTP_200_OK: GenerationDetailSerializer,
            status.HTTP_404_NOT_FOUND: {"description": "해당 기수를 찾을 수 없습니다."},
            status.HTTP_401_UNAUTHORIZED: {"description": "인증 실패 (로그인 필요)"},
            status.HTTP_403_FORBIDDEN: {"description": "권한 부족 (관리자/스태프 아님)"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "서버 내부 오류"},
        },
    )
    def get_queryset(self):
        queryset = Generation.objects.annotate(
            registered_students=Coalesce(
                Count("enrollment_requests", filter=Q(enrollment_requests__accepted_at__isnull=False)), 0
            )
        ).select_related("course")
        return queryset


# 기수 수정
@extend_schema(
    tags=["Admin - 기수관리"],
    summary="기수 수정 API",
)
class GenerationUpdateView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = GenerationUpdateSerializer
    lookup_field = "pk"

    @extend_schema(
        summary="기수 정보 수정",
        description="관리자 또는 스태프 권한으로 특정 기수의 수강 시작일과 수강 종료일을 수정합니다.",  # 설명 수정
        parameters=[
            OpenApiParameter(
                name="pk",  # URL 패턴의 <int:pk>와 일치하는 파라미터 이름
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="수정할 기수의 고유 ID",
                required=True,
            ),
        ],
        request=GenerationUpdateSerializer,  # 요청 바디의 스키마는 GenerationUpdateSerializer를 따름
        responses={
            status.HTTP_200_OK: GenerationUpdateSerializer,  # 성공 응답 스키마
            status.HTTP_400_BAD_REQUEST: {
                "description": "유효성 검증 실패 (잘못된 날짜 형식 또는 시작일이 종료일보다 늦음)"
            },  # 설명 수정
            status.HTTP_401_UNAUTHORIZED: {"description": "인증 실패 (로그인 필요)"},
            status.HTTP_403_FORBIDDEN: {"description": "권한 부족 (관리자/스태프 아님)"},
            status.HTTP_404_NOT_FOUND: {"description": "해당 기수를 찾을 수 없음"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "서버 내부 오류"},
        },
        examples=[
            OpenApiExample(
                "기수 시작/종료일 부분 수정 (PATCH)",  # PATCH 요청 예시
                value={"start_date": "2024-09-01", "end_date": "2025-02-28"},
                request_only=True,
                media_type="application/json",
            ),
            OpenApiExample(
                "기수 시작/종료일 전체 수정 (PUT)",  # PUT 요청 예시 (두 필드 모두 포함)
                value={"start_date": "2024-09-01", "end_date": "2025-02-28"},
                request_only=True,
                media_type="application/json",
            ),
        ],
    )
    def get_queryset(self):
        queryset = Generation.objects.select_related("course")
        return queryset

    def get_object(self):
        try:
            obj = super().get_object()
        except Http404:
            raise NotFound("해당 기수를 찾을 수 없습니다.")
        return obj


# 기수 삭제
@extend_schema(
    tags=["Admin - 기수관리"],
    summary="기수 삭제 API",
)
class GenerationDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    lookup_field = "pk"

    @extend_schema(
        summary="기수 삭제",
        description="관리자 또는 스태프 권한으로 특정 기수를 삭제합니다. 해당 기수에 등록된 수강생이 있는 경우 삭제할 수 없습니다.",
        parameters=[
            # Path Parameter로 기수 ID를 받음을 스웨거 문서에 명시합니다.
            OpenApiParameter(
                name="pk",  # URL 패턴의 <int:pk>와 일치하는 파라미터 이름
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="삭제할 기수의 고유 ID",
                required=True,
            ),
        ],
        # 삭제 성공 시 204 No Content 응답 (응답 바디 없음)
        responses={
            status.HTTP_204_NO_CONTENT: {"description": "기수가 성공적으로 삭제되었습니다."},
            status.HTTP_400_BAD_REQUEST: {
                "description": "해당 기수에 등록된 수강생이 있어 삭제할 수 없습니다."
            },  # <-- 새로운 400 에러 응답 추가!
            status.HTTP_401_UNAUTHORIZED: {"description": "인증 실패 (로그인 필요)"},
            status.HTTP_403_FORBIDDEN: {"description": "권한 부족 (관리자/스태프 아님)"},
            status.HTTP_404_NOT_FOUND: {"description": "해당 기수를 찾을 수 없음"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "서버 내부 오류"},
        },
    )
    def get_queryset(self):
        queryset = Generation.objects.select_related("course")
        return queryset

    def get_object(self):
        try:
            obj = super().get_object()
        except Http404:
            raise NotFound(detail="해당 기수를 찾을 수 없습니다.")
        return obj

    # perform_destroy 메서드를 오버라이드하여 삭제 전 조건 검사 추가!
    def perform_destroy(self, instance: Generation):
        if instance.students.exists():
            raise ValidationError("해당 기수에 등록된 수강생이 있어 삭제할 수 없습니다.")

        instance.delete()


@extend_schema(
    tags=["[Admin] 과정-기수 대시보드"],
    summary="과정 - 기수별 등록인원",
)
class CourseTrendView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
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


@extend_schema(
    tags=["[Admin] 과정-기수 대시보드"],
    summary="월별 등록인원",
)
class MonthlyCourseView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
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


@extend_schema(
    tags=["[Admin] 과정-기수 대시보드"],
    summary="운영중인 모든과정",
)
class OngoingCourseView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        # 활성화된 Generation을 select_related로 Course와 함께 가져옴 ( N + 1 문제 해결 )
        active_generations = Generation.objects.select_related("course").filter(
            ~Q(status=Generation.GenStatus.Finished) & ~Q(status=Generation.GenStatus.Ready)
        )

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
