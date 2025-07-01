from typing import Any, Dict, List

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import StudentEnrollmentRequest
from apps.users.serializers.admin_enrollments_serializers import (
    ApprovalResponseSerializer,
    EnrollmentRequestIdsSerializer,
    EnrollmentSerializer,
)


class AdminApproveEnrollmentsView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ApprovalResponseSerializer

    @extend_schema(
        request=EnrollmentRequestIdsSerializer,
        responses={200: ApprovalResponseSerializer},
        summary="어드민 수강신청 일괄 승인",
        description="선택한 ID 중 'PENDING' 상태인 수강신청을 승인합니다.",
        tags=["Admin - 수강 신청"],
    )
    def post(self, request: Request) -> Response:
        serializer = EnrollmentRequestIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids: List[int] = serializer.validated_data["ids"]

        now = timezone.now()

        mock_enrollment: List[StudentEnrollmentRequest] = [
            StudentEnrollmentRequest(
                id=id_,
                user_id=0,
                generation_id=0,
                status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED,
                accepted_at=now,
                created_at=now,
                updated_at=now,
            )
            for id_ in ids
        ]

        # 응답 메시지 및 serializer 구성
        message = f"{len(mock_enrollment)}건의 수강신청을 승인했습니다."
        response_data = {"approved_ids": [obj.id for obj in mock_enrollment], "message": message}

        response_serializer = ApprovalResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AdminEnrollmentListView(APIView):
    permission_classes = [IsAdminUser]  # 관리자 또는 스태프 권한만 접근 가능

    @extend_schema(
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="이메일, 닉네임, 이름, 과정명으로 검색"),
            OpenApiParameter(
                "status", OpenApiTypes.STR, enum=["PENDING", "APPROVED", "REJECTED"], description="수강신청 상태 필터링"
            ),
            OpenApiParameter(
                "ordering", OpenApiTypes.STR, description="정렬 기준: id, -id, created_at, -created_at 등"
            ),
            OpenApiParameter("limit", OpenApiTypes.INT, description="페이지네이션 - 페이지당 항목 수, 기본 10"),
            OpenApiParameter("offset", OpenApiTypes.INT, description="페이지네이션 - 시작 위치, 기본 0"),
        ],
        responses={200: EnrollmentSerializer(many=True)},
        tags=["Admin - 수강 신청"],
        summary="수강생 등록 신청 현황 목록 조회",
        description="수강생 등록 신청을 검색, 필터, 정렬해서 페이지네이션 포함 응답",
    )
    def get(self, request: Request) -> Response:
        # 검색어
        search = request.query_params.get("search", "").strip()
        # 상태 필터링
        status_filter = request.query_params.get("status")
        # 정렬 (기본값 id 순)
        ordering = request.query_params.get("ordering", "id")

        # 기본 queryset
        queryset = StudentEnrollmentRequest.objects.select_related("user", "generation", "generation__course")

        # 검색 조건 (이메일, 닉네임, 이름, 과정명)
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(user__nickname__icontains=search)
                | Q(user__name__icontains=search)
                | Q(generation__course__name__icontains=search)
            )

        # 상태 필터링
        if status_filter in ("PENDING", "APPROVED", "REJECTED"):
            queryset = queryset.filter(status=status_filter)

        queryset = queryset.order_by(ordering)

        # 페이징 (간단 예시: limit-offset)
        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))
        total = queryset.count()
        results = queryset[offset : offset + limit]

        serializer = EnrollmentSerializer(results, many=True)
        return Response(
            {
                "count": total,
                "next": offset + limit if offset + limit < total else None,
                "previous": offset - limit if offset - limit >= 0 else None,
                "results": serializer.data,
            }
        )
