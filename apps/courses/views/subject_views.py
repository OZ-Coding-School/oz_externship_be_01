import datetime
from typing import Any, Dict, List, Optional, Union, cast  # cast 추가!

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# apps.courses.models에서 실제 Subject, Course 모델 임포트 (타입 힌트용)
from apps.courses.models import Course, Subject
from apps.courses.serializers.subject_serializers import (
    SubjectDetailSerializer,
    SubjectListSerializer,
    SubjectSerializer,
    SubjectUpdateSerializer,
)


# --- MockCourse 클래스 정의 (MockSubject 외부로 이동하여 스코프 문제 해결) ---
# 이 클래스는 MockSubject.course 필드의 타입을 명확히 하고,
# Mypy가 이를 인식하도록 돕습니다.
class MockCourse:
    id: int
    name: str

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return self.name


# --- MockSubject 클래스 정의 (Mypy를 위한 Mock 모델) ---
class MockSubject:
    id: int
    title: str
    number_of_days: int
    number_of_hours: int
    course_name: str
    status: bool
    created_at: str
    updated_at: str
    thumbnail_img_url: str

    # course 필드를 MockCourse 또는 None으로 타입 힌트 (또는 Any)
    # 실제 Course 모델 인스턴스가 아니므로 MockCourse 또는 Any로 처리
    course: Optional[MockCourse]  # MockCourse로 변경

    _state: Any = None
    pk: int

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", 0)
        self.title = kwargs.get("title", "")
        self.number_of_days = kwargs.get("number_of_days", 0)
        self.number_of_hours = kwargs.get("number_of_hours", 0)
        self.course_name = kwargs.get("course_name", "")
        self.status = kwargs.get("status", False)
        self.created_at = kwargs.get("created_at", datetime.datetime.now().isoformat(timespec="seconds") + "Z")
        self.updated_at = kwargs.get("updated_at", datetime.datetime.now().isoformat(timespec="seconds") + "Z")
        self.thumbnail_img_url = kwargs.get("thumbnail_img_url", "")

        self.pk = self.id

        course_id = kwargs.get("course_id")
        course_name = kwargs.get("course_name")

        if course_id is not None and course_name is not None:
            self.course = MockCourse(id=course_id, name=course_name)
        else:
            self.course = None

    def __str__(self) -> str:
        return self.title


# --- SubjectListCreateAPIView ---
class SubjectListCreateAPIView(APIView):
    """
    (Admin) 과목 목록 조회 (GET) 및 등록 (POST) API.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="(Admin) 등록된 수강 과목 목록 조회",
        operation_id="subject_list",
        description="관리자 또는 스태프(운영 매니저 또는 러닝 코치) 권한의 유저는 어드민 페이지 내에서 등록된 수강 과목들을 목록으로 조회할 수 있습니다.",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="과목을 조회할 과정의 고유 ID로 필터링",
                required=False,
                examples=[OpenApiExample("과정 ID 필터링 예시", value="101")],
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="과목 활성화 여부로 필터링 (true/false)",
                required=False,
                examples=[
                    OpenApiExample("활성화 상태 필터링 예시 (true)", value="true"),
                    OpenApiExample("활성화 상태 필터링 예시 (false)", value="false"),
                ],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="title로 검색 (부분 일치)",
                required=False,
                examples=[OpenApiExample("제목 검색 예시", value="데이터베이스")],
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
        (Admin) 과목 목록을 조회합니다 (Mock 응답).
        """
        dummy_data: List[Dict[str, Any]] = [
            {
                "id": 1,
                "title": "데이터베이스 개론",
                "number_of_days": 4,
                "number_of_hours": 16,
                "course_id": 101,
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
                "course_id": 101,
                "course_name": "데이터베이스 심화 과정",
                "status": False,
                "created_at": "2025-06-23T11:00:00Z",
                "updated_at": "2025-06-23T11:00:00Z",
                "thumbnail_img_url": "http://example.com/sql_util.jpg",
            },
            {
                "id": 3,
                "title": "Python 프로그래밍 기초",
                "number_of_days": 5,
                "number_of_hours": 20,
                "course_id": 102,
                "course_name": "웹 개발 입문",
                "status": True,
                "created_at": "2025-06-24T09:00:00Z",
                "updated_at": "2025-06-24T09:00:00Z",
                "thumbnail_img_url": "http://example.com/python_intro.jpg",
            },
            {
                "id": 4,
                "title": "자료구조 알고리즘",
                "number_of_days": 7,
                "number_of_hours": 28,
                "course_id": 103,
                "course_name": "컴퓨터공학 심화",
                "status": True,
                "created_at": "2025-06-24T10:00:00Z",
                "updated_at": "2025-06-24T10:00:00Z",
                "thumbnail_img_url": "http://example.com/data_algo.jpg",
            },
        ]

        # List[MockSubject]를 List[Subject]로 명시적으로 캐스팅 (235번 오류 해결)
        mock_subjects: List[MockSubject] = [MockSubject(**item) for item in dummy_data]
        filtered_data: List[Subject] = cast(List[Subject], mock_subjects)  # cast 적용

        course_id_param: Optional[str] = request.query_params.get("course_id")
        status_param: Optional[str] = request.query_params.get("status")
        search_query: Optional[str] = request.query_params.get("search")

        if course_id_param:
            try:
                course_id_int: int = int(course_id_param)
                # MockSubject의 course.id에 접근하여 필터링
                # item.course가 None일 수 있으므로 안전하게 접근
                filtered_data = [item for item in filtered_data if item.course and item.course.id == course_id_int]
            except ValueError:
                raise ValidationError({"detail": "유효하지 않은 course_id입니다."})

        if status_param is not None:
            expected_status: bool = status_param.lower() in ["true", "1"]
            filtered_data = [item for item in filtered_data if item.status == expected_status]

        if search_query:
            search_query_lower: str = search_query.lower()
            filtered_data = [item for item in filtered_data if search_query_lower in item.title.lower()]

        serializer = SubjectListSerializer(filtered_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="(Admin) 새 과목 등록",
        operation_id="subject_create",
        description="관리자 권한으로 새로운 과목을 시스템에 등록합니다. 등록되는 과목은 특정 과정에 종속됩니다.",
        request=SubjectSerializer,
        examples=[
            OpenApiExample(
                "과목 등록 요청 예시",
                value={
                    "course_id": 101,
                    "title": "데이터베이스 개론",
                    "number_of_days": 4,
                    "number_of_hours": 16,
                    "thumbnail_img_url": "http://example.com/db_intro.jpg",
                    "status": True,
                },
                request_only=True,
                media_type="application/json",
            ),
            OpenApiExample(
                "과목 등록 성공 응답 예시 (201 OK)",
                value={
                    "id": 1,
                    "course_name": "데이터베이스 심화 과정",
                    "title": "데이터베이스 개론",
                    "number_of_days": 4,
                    "number_of_hours": 16,
                    "thumbnail_img_url": "http://example.com/db_intro.jpg",
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
        새로운 과목을 등록합니다 (Mock 응답).
        """
        serializer = SubjectSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        now: str = datetime.datetime.now().isoformat(timespec="seconds") + "Z"

        dummy_course_names: Dict[int, str] = {
            101: "데이터베이스 심화 과정",
            102: "웹 개발 입문",
            103: "컴퓨터공학 심화",
        }
        requested_course_id: Optional[int] = request.data.get("course_id")

        # requested_course_id가 None일 경우를 명시적으로 처리하여 arg-type 오류 해결 (360번 오류 해결)
        dummy_course_name: str
        if requested_course_id is not None:
            dummy_course_name = dummy_course_names.get(requested_course_id, "알 수 없는 과정")
        else:
            dummy_course_name = "알 수 없는 과정"

        dummy_response_data: Dict[str, Any] = {
            "id": 99,
            "course_name": dummy_course_name,
            "title": request.data.get("title"),
            "number_of_days": request.data.get("number_of_days"),
            "number_of_hours": request.data.get("number_of_hours"),
            "thumbnail_img_url": request.data.get("thumbnail_img_url"),
            "status": request.data.get("status", True),
            "created_at": now,
            "updated_at": now,
        }
        return Response(dummy_response_data, status=status.HTTP_201_CREATED)


# --- 과목 상세 조회, 수정, 삭제 API View ---
class SubjectDetailAPIView(APIView):
    """
    (Admin) 등록된 수강 과목 상세 조회 (GET), 수정 (PATCH), 삭제 (DELETE) API.
    """

    permission_classes = [AllowAny]

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
        특정 과목의 상세 정보를 조회합니다 (Mock 응답).
        """
        dummy_data_map: Dict[int, Dict[str, Any]] = {
            1: {
                "id": 1,
                "title": "데이터베이스 개론",
                "thumbnail_img_url": "http://example.com/db_intro.jpg",
                "course_id": 101,
                "course_name": "Mock Course 101",
                "number_of_days": 4,
                "number_of_hours": 16,
                "status": True,
                "created_at": "2025-06-23T10:30:00Z",
                "updated_at": "2025-06-23T10:30:00Z",
            },
            2: {
                "id": 2,
                "title": "SQL 활용",
                "thumbnail_img_url": "http://example.com/sql_advanced.jpg",
                "course_id": 101,
                "course_name": "데이터베이스 심화 과정",
                "number_of_days": 3,
                "number_of_hours": 12,
                "status": False,
                "created_at": "2025-06-23T11:00:00Z",
                "updated_at": "2025-06-23T11:00:00Z",
            },
        }

        data_dict = dummy_data_map.get(subject_id)
        if data_dict:
            # MockSubject 인스턴스를 Subject 타입으로 캐스팅 (483번 오류 해결)
            mock_instance: Subject = cast(Subject, MockSubject(**data_dict))
            serializer = SubjectDetailSerializer(mock_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotFound(detail=f"Subject with id '{subject_id}' not found.")

    @extend_schema(
        summary="(Admin) 등록된 수강 과목 상세 수정",
        operation_id="subject_partial_update",
        description="특정 ID를 가진 과목의 정보를 부분적으로 수정합니다.",
        request=SubjectUpdateSerializer,
        examples=[
            OpenApiExample(
                "과목 부분 수정 요청 예시",
                value={
                    "title": "데이터베이스 심화 (개정판)",
                    "thumbnail_img_url": "http://example.com/db_advanced_revised.jpg",
                    "number_of_days": 5,
                    "number_of_hours": 20,
                    "status": True,
                },
                request_only=True,
                media_type="application/json",
            ),
            OpenApiExample(
                "과목 부분 수정 성공 응답 예시 (200 OK)",
                value={
                    "id": 1,
                    "course_name": "데이터 베이스",
                    "title": "데이터베이스 심화 (개정판)",
                    "number_of_days": 5,
                    "number_of_hours": 20,
                    "thumbnail_img_url": "http://example.com/db_advanced_revised.jpg",
                    "status": True,
                    "created_at": "2025-06-23T10:30:00Z",
                    "updated_at": "2025-06-23T11:45:00Z",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
        responses={
            200: OpenApiResponse(response=SubjectSerializer, description="과목 부분 수정 성공"),
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
        특정 과목의 정보를 부분적으로 수정합니다 (Mock 응답).
        """
        dummy_original_data_map: Dict[int, Dict[str, Any]] = {
            1: {
                "id": 1,
                "title": "데이터베이스 개론",
                "thumbnail_img_url": "http://example.com/db_intro.jpg",
                "course_id": 101,
                "course_name": "데이터 베이스",
                "number_of_days": 4,
                "number_of_hours": 16,
                "status": True,
                "created_at": "2025-06-23T10:30:00Z",
                "updated_at": "2025-06-23T10:30:00Z",
            },
        }

        data_dict = dummy_original_data_map.get(subject_id)
        if not data_dict:
            raise NotFound(detail=f"Subject with id '{subject_id}' not found.")

        # 기존 MockSubject 인스턴스 생성 및 Subject 타입으로 캐스팅 (608번 오류 해결)
        instance: Subject = cast(Subject, MockSubject(**data_dict))

        serializer = SubjectUpdateSerializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Mock 인스턴스 업데이트 (실제 DB에 저장하는 대신)
        updated_data_from_serializer = serializer.validated_data
        for key, value in updated_data_from_serializer.items():
            setattr(instance, key, value)

        instance.updated_at = datetime.datetime.now().isoformat(timespec="seconds") + "Z"

        return Response(SubjectUpdateSerializer(instance).data, status=status.HTTP_200_OK)

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
        특정 과목을 삭제합니다 (Mock 응답).
        """
        if subject_id in [1, 2, 3]:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise NotFound(detail=f"Subject with id '{subject_id}' not found.")
