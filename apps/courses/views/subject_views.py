import datetime
from typing import Any, Dict, List, Optional, Union, cast  # 'cast' 임포트 확인

from django.http import QueryDict  # QueryDict 임포트 유지
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# 실제 Subject, Course 모델 임포트
from apps.courses.models import Course, Subject
from apps.courses.serializers.subject_serializers import (
    SubjectDetailSerializer,
    SubjectDropdownSerializer,
    SubjectListSerializer,
    SubjectSerializer,
    SubjectUpdateSerializer,
)
from apps.tests.permissions import IsAdminOrStaff


# --- SubjectListCreateAPIView ---
@extend_schema(
    tags=["Admin - 과목 관리"],
    summary="(Admin) 과목 목록 조회 (GET) 및 등록 (POST) API.",
    description="관리자 또는 스태프(운영 매니저 또는 러닝 코치) 권한의 유저는 어드민 페이지 내에서 등록된 수강 과목들을 목록으로 조회할 수 있습니다.",
)
class SubjectListCreateAPIView(APIView):
    """
    (Admin) 과목 목록 조회 (GET) 및 등록 (POST) API.
    """

    permission_classes = [IsAdminOrStaff]
    pagination_class = PageNumberPagination
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="(Admin) 등록된 수강 과목 목록 조회",
        operation_id="subject_list",
        description="관리자 또는 스태프(운영 매니저 또는 러닝 코치) 권한의 유저는 어드민 페이지 내에서 등록된 수강 과목들을 목록으로 조회할 수 있습니다. 페이지네이션 기능을 지원하며, 목록에서 조회 가능한 항목은 과목 고유 ID, 과목명, 수강 일수, 과목이 진행되는 시수, 과정명, 상태, 등록일시, 수정일시입니다.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="페이지 번호 (기본값: 1)",
                required=False,
                examples=[OpenApiExample("페이지 번호 예시", value="1")],
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="페이지당 항목 수 (기본값: 10)",
                required=False,
                examples=[OpenApiExample("페이지당 항목 수 예시", value="10")],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SubjectListSerializer(many=True),
                description="과목 목록 조회 성공",
                examples=[
                    OpenApiExample(
                        "과목 목록 조회 성공 응답 예시",
                        value=[
                            {
                                "id": 1,
                                "title": "데이터베이스 개론",
                                "number_of_days": 4,
                                "number_of_hours": 16,
                                "course_name": "데이터베이스 심화 과정",
                                "status": True,
                                "created_at": "2025-06-23T10:30:00Z",
                                "updated_at": "2025-06-23T10:30:00Z",
                                "thumbnail_img_url": "http://example.com/db_intro.jpg",
                            },
                            {
                                "id": 2,
                                "title": "SQL 활용",
                                "number_of_days": 3,
                                "number_of_hours": 12,
                                "course_name": "데이터베이스 심화 과정",
                                "status": False,
                                "created_at": "2025-06-23T11:00:00Z",
                                "updated_at": "2025-06-23T11:00:00Z",
                                "thumbnail_img_url": "http://example.com/sql_util.jpg",
                            },
                        ],
                        response_only=True,
                        status_codes=["200"],
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="유효하지 않은 쿼리 파라미터",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 값 예시",
                        value={"detail": "유효하지 않은 쿼리 파라미터입니다."},
                        response_only=True,
                        status_codes=["400"],
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        (Admin) 과목 목록을 조회합니다 (실제 DB 연동).
        """
        queryset = Subject.objects.all().select_related("course")

        query_params: QueryDict = request.query_params

        paginator = self.pagination_class()

        limit_param = query_params.get(cast(str, paginator.page_size_query_param))
        if limit_param:
            try:
                limit_value = int(limit_param)
                if limit_value <= 0:
                    raise ValidationError(
                        {"detail": f"유효하지 않은 쿼리 파라미터 '{paginator.page_size_query_param}' 값입니다."}
                    )
                paginator.page_size = limit_value
            except ValueError:
                raise ValidationError(
                    {"detail": f"유효하지 않은 쿼리 파라미터 '{paginator.page_size_query_param}' 값입니다."}
                )

        page_results = paginator.paginate_queryset(queryset, request, view=self)

        serializer = SubjectListSerializer(page_results, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="(Admin) 새 과목 등록",
        operation_id="subject_create",
        description="관리자 권한으로 새로운 과목을 시스템에 등록합니다. 등록되는 과목은 특정 과정에 종속됩니다.",
        request=SubjectSerializer,
        examples=[
            OpenApiExample(
                "과목 등록 요청 예시 (파일 포함)",
                value={
                    "course_id": 1,
                    "title": "데이터베이스 개론",
                    "number_of_days": 4,
                    "number_of_hours": 16,
                    "thumbnail_img_file": "파일 선택 (바이너리 데이터)",
                    "status": True,
                },
                request_only=True,
                media_type="multipart/form-data",
            ),
            OpenApiExample(
                "과목 등록 요청 예시 (파일 미포함)",
                value={
                    "course_id": 1,
                    "title": "네트워크 기초",
                    "number_of_days": 3,
                    "number_of_hours": 12,
                    "status": False,
                },
                request_only=True,
                media_type="multipart/form-data",
            ),
            OpenApiExample(
                "과목 등록 성공 응답 예시 (201 OK)",
                value={
                    "id": 1,
                    "course_name": "웹 개발 과정",
                    "title": "데이터베이스 개론",
                    "number_of_days": 4,
                    "number_of_hours": 16,
                    "thumbnail_img_url": "http://actual-s3-bucket.com/media/1/db_intro.jpg",
                    "status": True,
                    "created_at": "2025-06-23T10:30:00Z",
                    "updated_at": "2025-06-23T10:30:00Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
        responses={
            201: OpenApiResponse(response=SubjectSerializer, description="과목 등록 성공"),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="잘못된 요청 (유효성 검사 실패)",
                examples=[
                    OpenApiExample(
                        "과목 등록 실패 (필수 필드 누락) 예시",
                        value={"detail": "필수 필드 'title'이 누락되었습니다."},
                        response_only=True,
                        status_codes=["400"],
                    ),
                    OpenApiExample(
                        "과목 등록 실패 (제목 길이 초과) 예시",
                        value={"title": ["이 필드는 30자보다 길 수 없습니다."]},
                        response_only=True,
                        status_codes=["400"],
                    ),
                    OpenApiExample(
                        "과목 등록 실패 (Course ID 없음) 예시",
                        value={"course_id": ['유효하지 않은 pk "999" - 객체가 존재하지 않습니다.']},
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        새로운 과목을 등록합니다 (실제 DB 연동).
        """
        serializer = SubjectSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()

        response_serializer = SubjectSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# --- 과목 상세 조회, 수정, 삭제 API View ---
@extend_schema(
    tags=["Admin - 과목 관리"],
    summary="(Admin) 등록된 수강 과목 상세 조회, 수정, 삭제 API.",
    description="관리자 권한으로 특정 과목의 상세 정보를 조회, 수정, 삭제합니다.",
)
class SubjectDetailAPIView(APIView):
    """
    (Admin) 등록된 수강 과목 상세 조회 (GET), 수정 (PATCH), 삭제 (DELETE) API.
    """

    permission_classes = [IsAdminOrStaff]
    parser_classes = [MultiPartParser, FormParser]

    # 객체를 가져오는 헬퍼 메서드
    def get_object(self, subject_id: int) -> Subject:
        try:
            return Subject.objects.select_related("course").get(id=subject_id)
        except Subject.DoesNotExist:
            raise NotFound(detail=f"Subject with id '{subject_id}' not found.")

    @extend_schema(
        summary="(Admin) 등록된 수강 과목 상세 조회",
        operation_id="subject_retrieve",
        description="관리자 권한으로 특정 과목의 상세 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=SubjectDetailSerializer,
                description="과목 상세 조회 성공",
                examples=[
                    OpenApiExample(
                        "과목 상세 조회 성공 응답 예시",
                        value={
                            "id": 1,
                            "title": "데이터베이스 개론",
                            "thumbnail_img_url": "http://example.com/db_intro.jpg",
                            "course_name": "Mock Course 101",
                            "number_of_days": 4,
                            "number_of_hours": 16,
                            "status": True,
                            "created_at": "2025-06-23T10:30:00Z",
                            "updated_at": "2025-06-23T10:30:00Z",
                        },
                        response_only=True,
                        status_codes=["200"],
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="과목을 찾을 수 없음",
                examples=[
                    OpenApiExample(
                        "과목 상세 조회 실패 (404) 응답 예시",
                        value={"detail": "Subject with id '1' not found."},
                        response_only=True,
                        status_codes=["404"],
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, subject_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        특정 과목의 상세 정보를 조회합니다 (실제 DB 연동).
        """
        instance = self.get_object(subject_id)
        serializer = SubjectDetailSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="(Admin) 등록된 수강 과목 상세 수정",
        operation_id="subject_partial_update",
        description="특정 ID를 가진 과목의 정보를 부분적으로 수정합니다.",
        request=SubjectUpdateSerializer,
        examples=[
            OpenApiExample(
                "과목 부분 수정 요청 예시 (파일 포함)",
                value={
                    "title": "데이터베이스 심화 (개정판)",
                    "thumbnail_img_file": "파일 선택 (바이너리 데이터)",
                    "number_of_days": 5,
                    "number_of_hours": 20,
                    "status": True,
                },
                request_only=True,
                media_type="multipart/form-data",
            ),
            OpenApiExample(
                "과목 부분 수정 요청 예시 (파일 미포함)",
                value={
                    "title": "데이터베이스 심화 (개정판)",
                    "number_of_days": 5,
                    "number_of_hours": 20,
                    "status": True,
                },
                request_only=True,
                media_type="multipart/form-data",
            ),
            OpenApiExample(
                "과목 부분 수정 성공 응답 예시 (200 OK)",
                value={
                    "id": 1,
                    "course_name": "데이터 베이스",
                    "title": "데이터베이스 심화 (개정판)",
                    "number_of_days": 5,
                    "number_of_hours": 20,
                    "thumbnail_img_url": "http://actual-s3-bucket.com/media/db_advanced_revised.jpg",
                    "status": True,
                    "created_at": "2025-06-23T10:30:00Z",
                    "updated_at": "2025-06-23T11:45:00Z",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
        responses={
            200: OpenApiResponse(response=SubjectUpdateSerializer, description="과목 부분 수정 성공"),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="잘못된 요청 (유효성 검사 실패)",
                examples=[
                    OpenApiExample(
                        "과목 부분 수정 실패 (필수 필드 누락) 예시",
                        value={"detail": "필수 필드 'title'이 누락되었습니다."},
                        response_only=True,
                        status_codes=["400"],
                    ),
                    OpenApiExample(
                        "과목 부분 수정 실패 (제목 길이 초과) 예시",
                        value={"title": ["이 필드는 30자보다 길 수 없습니다."]},
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="과목을 찾을 수 없음",
                examples=[
                    OpenApiExample(
                        "과목 수정 실패 (404) 응답 예시",
                        value={"detail": "Subject with id '1' not found."},
                        response_only=True,
                        status_codes=["404"],
                    )
                ],
            ),
        },
    )
    def patch(self, request: Request, subject_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        특정 과목의 정보를 부분적으로 수정합니다 (실제 DB 연동).
        """
        instance = self.get_object(subject_id)
        serializer = SubjectUpdateSerializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = serializer.save()

        response_serializer = SubjectUpdateSerializer(updated_instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="(Admin) 수강 과목 삭제",
        operation_id="subject_delete",
        description="관리자 권한으로 특정 과목을 시스템에서 삭제합니다.",
        responses={
            204: OpenApiResponse(
                response=None,
                description="과목 삭제 성공 (콘텐츠 없음)",
                examples=[
                    OpenApiExample("과목 삭제 성공 응답 예시", value=None, response_only=True, status_codes=["204"])
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="과목을 찾을 수 없음",
                examples=[
                    OpenApiExample(
                        "과목 삭제 실패 (404) 응답 예시",
                        value={"detail": "Subject with id '1' not found."},
                        response_only=True,
                        status_codes=["404"],
                    )
                ],
            ),
        },
    )
    def delete(self, request: Request, subject_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        특정 과목을 삭제합니다 (실제 DB 연동).
        """
        instance = self.get_object(subject_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- SubjectDropdownListAPIView (프론트 요청) ---
@extend_schema(
    tags=["Admin - 과목 관리"],
    summary="(Admin) 특정 과정의 과목 목록 조회 API (상태 필터링)",
    description="관리자 또는 스태프 권한의 유저는 어드민 페이지 내에서 특정 과정에 속한 과목 목록을 드롭다운 선택을 위해 조회할 수 있습니다. 이때 과목의 상태(활성화 여부)로 필터링할 수 있습니다.",
)
class SubjectDropdownListAPIView(APIView):
    """
    (Admin) 특정 과정의 과목 목록 조회 API (상태 필터링).
    드롭다운 목록에 필요한 'id'와 'title' 필드만 반환합니다.
    """

    permission_classes = [IsAdminOrStaff]  # TODO: 실제 권한 (Staff, Admin)으로 변경 필요

    @extend_schema(
        summary="(Admin) 특정 과정의 과목 목록 조회 (드롭다운)",
        operation_id="subject_dropdown_list",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="과목 목록을 조회할 과정의 고유 ID",
                required=True,
                examples=[OpenApiExample("Course ID 예시", value=1)],
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="과목 활성화 여부로 필터링 (true/false). 이 파라미터가 제공되지 않으면 모든 상태의 과목을 반환합니다.",
                required=False,
                examples=[
                    OpenApiExample("활성화 상태 필터링 예시 (true)", value="true"),
                    OpenApiExample("비활성화 상태 필터링 예시 (false)", value="false"),
                ],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SubjectDropdownSerializer(many=True),
                description="과목 목록 조회 성공",
                examples=[
                    OpenApiExample(
                        "과목 목록 조회 성공 응답 예시",
                        value=[
                            {"id": 101, "title": "데이터베이스 기초"},
                            {"id": 102, "title": "SQL 심화"},
                        ],
                        response_only=True,
                        status_codes=["200"],
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="잘못된 요청 (유효성 검사 실패)",
                examples=[
                    OpenApiExample(
                        "잘못된 쿼리 파라미터 예시",
                        value={"detail": "잘못된 쿼리 파라미터 값입니다. 'status'는 'true' 또는 'false'여야 합니다."},
                        response_only=True,
                        status_codes=["400"],
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="인증 토큰 유효하지 않음",
                examples=[
                    OpenApiExample(
                        "인증 실패 예시",
                        value={"detail": "인증 토큰이 유효하지 않습니다."},
                        response_only=True,
                        status_codes=["401"],
                    )
                ],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 없음 예시",
                        value={"detail": "해당 작업에 대한 관리자 또는 스태프 권한이 없습니다."},
                        response_only=True,
                        status_codes=["403"],
                    )
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="과정을 찾을 수 없음",
                examples=[
                    OpenApiExample(
                        "과정 없음 예시",
                        value={"detail": "해당 course_id를 가진 과정을 찾을 수 없습니다."},
                        response_only=True,
                        status_codes=["404"],
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, course_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        특정 과정에 속한 과목 목록을 조회합니다 (드롭다운 용도).
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound(detail=f"해당 course_id({course_id})를 가진 과정을 찾을 수 없습니다.")

        queryset = Subject.objects.filter(course=course)

        status_param: Optional[str] = request.query_params.get(cast(str, "status"))

        if status_param is not None:
            if status_param.lower() in ["true", "false"]:
                expected_status: bool = status_param.lower() == "true"
                queryset = queryset.filter(status=expected_status)
            else:
                raise ValidationError(
                    {"detail": "잘못된 쿼리 파라미터 값입니다. 'status'는 'true' 또는 'false'여야 합니다."}
                )

        serializer = SubjectDropdownSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
