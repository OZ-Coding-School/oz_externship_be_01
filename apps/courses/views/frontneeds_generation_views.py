from typing import Any, Dict, List, Optional, Union

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

# 필요한 모델 및 시리얼라이저 임포트
from apps.courses.models import Course, Generation
from apps.courses.serializers.frontneeds_generation_serializer import (
    GenerationDropdownSerializer,
)


# --- GenerationDropdownListAPIView (새로 추가) ---
@extend_schema(
    tags=["Admin - 기수 관리"],
    summary="(Admin) 특정 과정의 기수 목록 조회 API",
    description="관리자 또는 스태프 권한의 유저는 어드민 페이지 내에서 특정 과정에 속한 모든 기수(Generation)의 목록을 드롭다운 선택을 위해 조회할 수 있습니다.",
)
class GenerationDropdownListAPIView(APIView):
    """
    (Admin) 특정 과정의 기수 목록 조회 API.
    드롭다운 목록에 필요한 'id'와 'name' 필드만 반환합니다.
    """

    permission_classes = [AllowAny]  # TODO: 실제 권한 (Staff, Admin)으로 변경 필요

    @extend_schema(
        summary="(Admin) 특정 과정의 기수 목록 조회 (드롭다운)",
        operation_id="v1_admin_generations_dropdown_list",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="기수 목록을 조회할 과정의 고유 ID",
                required=True,
                examples=[OpenApiExample("Course ID 예시", value=1)],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=GenerationDropdownSerializer(many=True),
                description="기수 목록 조회 성공",
                examples=[
                    OpenApiExample(
                        "기수 목록 조회 성공 응답 예시",
                        value=[
                            {"id": 11, "name": "11기"},
                            {"id": 12, "name": "12기"},
                        ],
                        response_only=True,
                        status_codes=["200"],
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
        특정 과정에 속한 기수 목록을 조회합니다 (드롭다운 용도).
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound(detail=f"해당 course_id({course_id})를 가진 과정을 찾을 수 없습니다.")

        queryset = Generation.objects.filter(course=course)

        serializer = GenerationDropdownSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
