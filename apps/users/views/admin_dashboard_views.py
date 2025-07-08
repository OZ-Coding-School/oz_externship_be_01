from datetime import datetime, timedelta
from typing import Any, Dict, List, OrderedDict, TypedDict, Union

from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff
from apps.users.models import StudentEnrollmentRequest, User
from apps.users.serializers.admin_dashboard_serializers import (
    ChartTypeEnum,
    ConversionTrendResponseSerializer,
    JoinTrendQuerySerializer,
    JoinTrendResponseSerializer,
    TrendQuerySerializer,
    WithdrawalReasonResponseSerializer,
    WithdrawalReasonTrendResponseSerializer,
)


# 수강생 전환 추이 분석 차트
class AdminEnrollmentTrendView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        request=TrendQuerySerializer,
        responses={200: ConversionTrendResponseSerializer},
        summary="수강생 전환 추세 조회",
        description="월별 또는 년별 단위로 수강생 전환 수를 그래프 데이터 형태로 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="unit",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="단위: 'monthly' 또는 'yearly'",
            )
        ],
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        serializer = TrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data["unit"]

        # 유저별 최초 승인일만 추출
        first_approved_qs = (
            StudentEnrollmentRequest.objects.filter(
                status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED,
                accepted_at__isnull=False,
                user=OuterRef("user"),
            )
            .order_by("accepted_at", "id")
            .values("id")[:1]
        )

        # 이 id와 같은 승인 이력만 필터링
        base_qs = StudentEnrollmentRequest.objects.filter(id__in=Subquery(first_approved_qs))

        labels: List[str] = []
        data: List[int] = []

        if unit == "monthly":
            qs_monthly: List[Dict[str, Any]] = list(
                base_qs.annotate(period=TruncMonth("accepted_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )

            for item in qs_monthly:
                label = item["period"].strftime("%Y-%m")
                labels.append(label)
                data.append(item["count"])

            range_ = "last_12_months"

        else:  # yearly
            qs_yearly: List[Dict[str, Any]] = list(
                base_qs.annotate(period=TruncYear("accepted_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )

            for item in qs_yearly:
                label = item["period"].strftime("%Y")
                labels.append(label)
                data.append(item["count"])

            range_ = "last_4_years"

        response_data = {
            "title": f"수강생 전환 추세 {labels[0]} ~ {labels[-1]}" if labels else "수강생 전환 추세",
            "graph_type": "student_conversion",
            "chart_type": ChartTypeEnum.BAR.value,
            "range": range_,
            "data": OrderedDict(zip(labels, data)),
        }

        return Response(response_data, status=status.HTTP_200_OK)


# 회원가입 추세 그래프
class AdminJoinTrendView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        request=JoinTrendQuerySerializer,
        responses={200: JoinTrendResponseSerializer},
        summary="회원가입 추세 그래프 데이터 조회",
        description="일별/월별/연도별 회원가입 수를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="range_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="단위: 'daily' 또는 'monthly' 또는 'yearly'",
            )
        ],
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        serializer = JoinTrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        range_type = serializer.validated_data["range_type"]

        today = datetime.today()
        base_qs = User.objects.all()

        labels: List[str] = []
        raw_counts: Dict[str, int] = {}

        if range_type == "daily":
            start_date = today - timedelta(days=29)
            qs_daily: List[Dict[str, Any]] = list(
                base_qs.filter(created_at__date__gte=start_date.date())
                .annotate(period=TruncDay("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
            raw_counts = {item["period"].strftime("%Y-%m-%d"): item["count"] for item in qs_daily}

        elif range_type == "monthly":
            start_month = (today.replace(day=1) - timedelta(days=365)).replace(day=1)
            qs_monthly: List[Dict[str, Any]] = list(
                base_qs.filter(created_at__date__gte=start_month.date())
                .annotate(period=TruncMonth("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = []
            for m in range(12):
                dt = start_month + timedelta(days=30 * m)
                labels.append(dt.strftime("%Y-%m"))
            raw_counts = {item["period"].strftime("%Y-%m"): item["count"] for item in qs_monthly}

        elif range_type == "yearly":
            start_year = today.year - 4
            qs_yearly: List[Dict[str, Any]] = list(
                base_qs.filter(created_at__year__gte=start_year)
                .annotate(period=TruncYear("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [str(y) for y in range(start_year, today.year + 1)]
            raw_counts = {item["period"].strftime("%Y"): item["count"] for item in qs_yearly}

        # 누락된 구간은 0으로 채움
        data = OrderedDict((label, raw_counts.get(label, 0)) for label in labels)

        # chart_type 조건 설정
        if range_type == "daily":
            chart_type = ChartTypeEnum.LINE.value
        else:
            chart_type = ChartTypeEnum.BAR.value

        return Response(
            {
                "title": f"회원가입 추세 {labels[0]} ~ {labels[-1]}" if labels else "회원가입 추세",
                "graph_type": "join",
                "chart_type": chart_type,
                "range": range_type,
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class AdminWithdrawTrendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=TrendQuerySerializer,
        responses={200: ConversionTrendResponseSerializer},
        summary="회원 탈퇴 추세 조회",
        description="월별 또는 년별 단위로 회원 탈퇴 수를 그래프 데이터 형태로 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        serializer = TrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data["unit"]

        if unit == "monthly":
            labels = [f"2024-{m:02}" for m in range(7, 13)] + [f"2025-{m:02}" for m in range(1, 7)]
            data = [1, 0, 2, 1, 0, 3, 1, 2, 0, 1, 2, 3]
            range_ = "last_12_months"
        else:
            labels = [str(y) for y in range(2021, 2025)]
            data = [10, 13, 8, 15]
            range_ = "last_4_years"

        return Response(
            {
                "title": f"회원 탈퇴 추세 {labels[0]} ~ {labels[-1]}",
                "graph_type": "withdraw",
                "chart_type": ChartTypeEnum.BAR.value,
                "range": range_,
                "data": dict(zip(labels, data)),
            },
            status=status.HTTP_200_OK,
        )


# 탈퇴 사유 항목 타입 정의
class WithdrawalReasonItem(TypedDict):
    reason: str
    count: int


class AdminWithdrawalReasonPieView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: WithdrawalReasonResponseSerializer},
        summary="회원 탈퇴 사유 통계 조회",
        description="최근 6개월 내 탈퇴 사유를 집계하여 원형 차트용 데이터를 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        raw_data: List[WithdrawalReasonItem] = [
            {"reason": "콘텐츠 불만족", "count": 12},
            {"reason": "가격 문제", "count": 10},
            {"reason": "기타", "count": 8},
        ]

        total = sum(item["count"] for item in raw_data)
        enriched_data: List[Dict[str, Union[str, int, float]]] = [
            {
                "reason": item["reason"],
                "count": item["count"],
                "percentage": round(item["count"] / total * 100, 1),
            }
            for item in raw_data
        ]

        return Response(
            {
                "title": "탈퇴 사유 비율 2024-01 ~ 2024-06",
                "graph_type": "withdraw_reason",
                "chart_type": ChartTypeEnum.PIE.value,
                "range": "last_6_months",
                "data": enriched_data,
            },
            status=status.HTTP_200_OK,
        )


class AdminWithdrawalReasonTrendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: WithdrawalReasonTrendResponseSerializer},
        summary="탈퇴 사유 월별 추이 그래프 조회",
        description="최근 12개월간 특정 탈퇴 사유의 월별 발생 수를 조회하여 bar 또는 line 차트용 데이터로 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        reason = request.query_params.get("reason", "기타")
        chart_type = request.query_params.get("chart_type", ChartTypeEnum.BAR.value)

        labels = [f"2024-{m:02}" for m in range(7, 13)] + [f"2025-{m:02}" for m in range(1, 7)]
        data = [(i * 2 + 1) % 5 for i in range(12)]

        return Response(
            {
                "title": f"{reason} 탈퇴 사유 추이 {labels[0]} ~ {labels[-1]}",
                "graph_type": "withdraw_reason",
                "chart_type": chart_type,
                "range": "last_12_months",
                "reason": reason,
                "data": dict(zip(labels, data)),
            },
            status=status.HTTP_200_OK,
        )
