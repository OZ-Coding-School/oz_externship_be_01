from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import StudentEnrollmentRequest, User
from apps.users.serializers.admin_enrollments_list_serializers import (
    AdminEnrollmentSerializer,
)


class AdminEnrollmentPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class AdminEnrollmentListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminEnrollmentPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="한 페이지에 표시할 항목 수 (기본값: 10)",
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="건너뛸 항목 수 (예: 0 → 처음부터, 10 → 11번째부터)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="정렬 기준 (예: id, -id, created_at, -created_at)",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="이메일, 닉네임, 이름, 과정명 중 일부 키워드로 검색",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                enum=["PENDING", "APPROVED", "REJECTED"],
                location=OpenApiParameter.QUERY,
                description="수강신청 상태 필터링 (대기중, 승인됨, 반려됨)",
            ),
        ],
        summary="수강생 등록 신청 현황 목록 조회",
        description="스태프/관리자 권한으로 수강신청 내역을 검색, 정렬, 필터링하여 조회",
        tags=["Admin - 수강 신청"],
    )
    def get(self, request):
        user = request.user
        if user.role not in [User.Role.ADMIN, User.Role.TA, User.Role.OM, User.Role.LC]:
            return Response({"detail": "접근 권한이 없습니다."}, status=403)

        search = request.query_params.get("search", "").strip()
        status_filter = request.query_params.get("status")
        ordering = request.query_params.get("ordering", "id")

        queryset = StudentEnrollmentRequest.objects.select_related("user", "generation", "generation__course")

        # 검색필터
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(user__nickname__icontains=search)
                | Q(user__name__icontains=search)
                | Q(generation__course__name__icontains=search)
            )

        # 상태
        status_filter = request.query_params.get("status")
        valid_statuses = StudentEnrollmentRequest.EnrollmentStatus.values

        if status_filter:
            if status_filter not in valid_statuses:
                return Response({"detail": f"잘못된 상태 값입니다. 허용된 값: {valid_statuses}"}, status=400)
            queryset = queryset.filter(status=status_filter)

        # 정렬
        ordering = request.query_params.get("ordering", "id")
        valid_orderings = {"id", "-id", "created_at", "-created_at"}
        if ordering not in valid_orderings:
            return Response({"detail": f"잘못된 정렬 기준입니다. 허용된 값: {sorted(valid_orderings)}"}, status=400)
        queryset = queryset.order_by(ordering)

        # 페이지네이션
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AdminEnrollmentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
