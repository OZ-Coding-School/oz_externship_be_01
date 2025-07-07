import uuid

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import parsers, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Subject

# 내부 앱 - models
from apps.tests.models import Test, TestQuestion
from apps.tests.pagination import AdminTestListPagination
from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_serializers import (
    AdminTestUpdateSerializer,
    TestCreateSerializer,
    TestDetailSerializer,
    TestListSerializer,
)
from core.utils.s3_file_upload import S3Uploader


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 삭제 API",
    description=(
        "관리자 또는 스태프 권한으로 특정 쪽지시험(Test)을 삭제합니다.\n"
        "- 연결된 문제(TestQuestion)는 함께 삭제되며,\n"
        "- S3에 업로드된 썸네일 이미지도 함께 삭제됩니다.\n"
        "- 배포(TestDeployment), 응시(TestSubmission)는 보존됩니다."
    ),
    responses={
        204: OpenApiResponse(description="삭제 성공 - 응답 본문 없음"),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="해당 리소스를 삭제할 권한이 없습니다."),
        404: OpenApiResponse(description="Test not found."),
    },
)
# 쪽지시험 삭제 API ( Test 및 연결된 TestQuestion Hard Delete / TestDeployment, TestSubmission은 보존)
# S3에 업로드된 썸네일 이미지 파일도 함께 삭제
class AdminTestDeleteAPIView(APIView):

    permission_classes = [IsAdminOrStaff]

    def delete(self, request: Request, test_id: int) -> Response:

        try:
            # 삭제 대상 쪽지시험 조회
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # S3에 업로드된 썸네일 이미지 삭제
        if test.thumbnail_img_url:
            uploader = S3Uploader()
            if not uploader.delete_file(test.thumbnail_img_url):
                print("[WARNING] S3 이미지 삭제 실패")

        # Test와 연결된 문제(TestQuestion)는 CASCADE로 Hard Delete 처리
        test.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# (admin)쪽지시험 수정
@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 수정 API",
    description="관리자/스태프 권한으로 등록된 쪽지시험의 제목, 과목, 썸네일 이미지를 수정합니다.",
    responses={
        200: AdminTestUpdateSerializer,
        400: OpenApiResponse(description="Invalid subject ID."),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        404: OpenApiResponse(description="Test not found."),
    },
)
class AdminTestUpdateAPIView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = AdminTestUpdateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def patch(self, request, test_id: int):
        # 단일 쿼리 최적화 및 수정 후 상세 응답 직렬화 시 문제 리스트까지 한꺼번에 가져오기
        try:
            test = Test.objects.select_related("subject").prefetch_related("questions").get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=test, data=request.data, partial=True)
        #  # subject_id 유효성 검증까지 처리
        serializer.is_valid(raise_exception=True)

        # 수정 및 updated_at 갱신
        updated_test = serializer.save()
        response_serializer = self.serializer_class(updated_test)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# (admin)쪽지시험 상세조회


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 상세조회 API",
    description="관리자/스태프 권한으로 등록된 특정 쪽지시험 상세 정보를 조회합니다.",
    responses={
        200: TestDetailSerializer,
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        404: OpenApiResponse(description="Test not found."),
    },
)
class AdminTestDetailAPIView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = TestDetailSerializer

    def get(self, request, test_id: int):
        try:
            # Test + subject select_related, questions prefetch_related로 N+1 방지
            test = Test.objects.select_related("subject").prefetch_related("questions").get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        # context 전달 하지 않고 바로 접근
        serializer = self.serializer_class(test)

        return Response(serializer.data, status=status.HTTP_200_OK)


# (admin)쪽지시험 목록조회


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 목록조회 API",
    description=(
        "관리자/스태프 권한으로 등록된 쪽지시험 목록을 조회합니다.\n\n"
        "- generation_id(과정별 필터링), search(시험명/과목명 검색), ordering(정렬: recent/alphabetical) 지원\n"
        "- 페이지네이션 적용"
    ),
    parameters=[
        OpenApiParameter(
            name="course_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="특정 과정 ID로 필터링",
        ),
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            description="시험명 또는 과목명으로 검색 (부분/완전일치 모두 지원)",
        ),
        OpenApiParameter(
            name="ordering",
            type=str,
            location=OpenApiParameter.QUERY,
            enum=["recent", "alphabetical"],
            description="정렬 옵션: recent(최신순, 기본), alphabetical(가나다순)",
        ),
        OpenApiParameter(
            name="page",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본 1)",
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지당 항목 수 (기본 10, 최대 100)",
        ),
    ],
    responses={
        200: OpenApiResponse(description="조회 성공"),
        401: OpenApiResponse(description="인증 정보가 없거나 유효하지 않습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
    },
)
class AdminTestListView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = TestListSerializer

    def get(self, request: Request) -> Response:
        queryset = Test.objects.select_related("subject", "subject__course").annotate(
            question_count=Count("questions", distinct=True),
            submission_count=Count("deployments__submissions", distinct=True),
        )

        # 기존 generation_id 필터 제거 후 course_id 필터로 교체
        course_id = request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(subject__course__id=course_id)

        # 검색: 시험명 또는 과목명 ( 부분 + 완전일치 검색 적용)
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(subject__title__icontains=search)
                | Q(title__iexact=search)
                | Q(subject__title__iexact=search)
            )

        # 정렬: 최신순(기본), 가나다순
        ordering = request.query_params.get("ordering", "recent")
        if ordering == "alphabetical":
            queryset = queryset.order_by("title")
        else:  # 기본 최신순
            queryset = queryset.order_by("-created_at")

        # 페이지네이션
        paginator = AdminTestListPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)


# (admin)쪽지시험 생성


@extend_schema(
    tags=["[Admin] Test - Test (쪽지시험 생성/조회/수정/삭제)"],
    summary="쪽지시험 생성 API",
    description="JWT 인증이 필요하며, 관리자/스태프 권한을 가진 사용자만 접근할 수 있습니다.",
    request={"multipart/form-data": TestCreateSerializer},
)
class AdminTestCreateAPIView(APIView):
    serializer_class = TestCreateSerializer
    permission_classes = [IsAdminOrStaff]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        test = serializer.save()

        response_serializer = self.serializer_class(instance=test)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
