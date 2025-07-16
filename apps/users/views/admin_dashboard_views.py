from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, List, TypedDict, Union, cast

from dateutil.relativedelta import relativedelta
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff
from apps.users.models import StudentEnrollmentRequest, User, Withdrawal
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

        if range_type == "daily":
            start_date = today - timedelta(days=29)
            qs_daily = list(
                base_qs.filter(created_at__date__gte=start_date.date())
                .annotate(period=TruncDay("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
            raw_counts = {item["period"].strftime("%Y-%m-%d"): item["count"] for item in qs_daily}

        elif range_type == "monthly":
            start_month = (today.replace(day=1) - relativedelta(months=12)).replace(day=1)
            qs_monthly = list(
                base_qs.filter(created_at__date__gte=start_month.date())
                .annotate(period=TruncMonth("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [(start_month + relativedelta(months=m)).strftime("%Y-%m") for m in range(13)]
            raw_counts = {item["period"].strftime("%Y-%m"): item["count"] for item in qs_monthly}

        elif range_type == "yearly":
            start_year = today.year - 4
            qs_yearly = list(
                base_qs.filter(created_at__year__gte=start_year)
                .annotate(period=TruncYear("created_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [str(y) for y in range(start_year, today.year + 1)]
            raw_counts = {item["period"].strftime("%Y"): item["count"] for item in qs_yearly}

        else:
            raise ValidationError("range_type은 'daily', 'monthly', 'yearly' 중 하나여야 합니다.")

        # 누락된 구간은 0으로 채움
        data = OrderedDict((label, raw_counts.get(label, 0)) for label in labels)

        # chart_type 조건 설정
        chart_type = ChartTypeEnum.LINE.value if range_type == "daily" else ChartTypeEnum.BAR.value

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


# 탈퇴 추이 그래프
class AdminWithdrawTrendView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        request=TrendQuerySerializer,
        responses={200: ConversionTrendResponseSerializer},
        summary="회원 탈퇴 추세 조회",
        description="월별 또는 년별 단위로 회원 탈퇴 수를 그래프 데이터 형태로 반환합니다.",
        tags=["Admin - 유저 대시보드"],
        parameters=[
            OpenApiParameter(
                name="unit",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="단위: 'monthly' 또는 'yearly'",
            )
        ],
    )
    def get(self, request: Request) -> Response:
        serializer = TrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data["unit"]

        today = datetime.today()
        base_qs = Withdrawal.objects.all()

        labels: List[str] = []

        if unit == "monthly":
            start_month = today.replace(day=1) - relativedelta(years=1)
            qs_monthly = list(
                base_qs.filter(updated_at__date__gte=start_month.date())
                .annotate(period=TruncMonth("updated_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            for i in range(13):
                month = start_month + relativedelta(months=i)
                labels.append(month.strftime("%Y-%m"))
            raw_counts = {item["period"].strftime("%Y-%m"): item["count"] for item in qs_monthly}
            range_ = "last_12_months"

        elif unit == "yearly":
            start_year = today - relativedelta(years=4)
            qs_yearly = list(
                base_qs.filter(updated_at__date__gte=start_year.date())
                .annotate(period=TruncYear("updated_at"))
                .values("period")
                .annotate(count=Count("id"))
                .order_by("period")
            )
            labels = [str(start_year.year + i) for i in range(5)]
            raw_counts = {item["period"].strftime("%Y"): item["count"] for item in qs_yearly}
            range_ = "last_4_years"

        else:
            raise ValidationError("unit은 'monthly' 또는 'yearly' 중 하나여야 합니다.")

        data = OrderedDict((label, raw_counts.get(label, 0)) for label in labels)

        return Response(
            {
                "title": f"회원 탈퇴 추세 {labels[0]} ~ {labels[-1]}" if labels else "회원 탈퇴 추세",
                "graph_type": "withdraw",
                "chart_type": ChartTypeEnum.BAR.value,
                "range": range_,
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


# 탈퇴 사유 추이 원형 그래프
class AdminWithdrawalReasonPieView(APIView):
    permission_classes = [IsAdminOrStaff]  # 어드민 권한

    @extend_schema(
        responses={200: WithdrawalReasonResponseSerializer},
        summary="회원 탈퇴 사유 통계 조회",
        description="최근 6개월 내 탈퇴 사유를 집계하여 원형 차트용 데이터를 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        today = datetime.today()
        six_months_ago = (today.replace(day=1) - relativedelta(months=6)).date()

        # 최근 6개월간 탈퇴 사유 집계
        qs = (
            Withdrawal.objects.filter(created_at__date__gte=six_months_ago)
            .values("reason")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        total = sum(item["count"] for item in qs)
        enriched_data: List[Dict[str, Union[str, int, float]]] = [
            {
                "reason": str(Withdrawal.Reason(item["reason"]).label),
                "count": item["count"],
                "percentage": round(item["count"] / total * 100, 1) if total else 0,
            }
            for item in qs
        ]

        return Response(
            {
                "title": f"탈퇴 사유 비율 {six_months_ago.strftime('%Y-%m')} ~ {today.strftime('%Y-%m')}",
                "graph_type": "withdraw_reason",
                "chart_type": ChartTypeEnum.PIE.value,
                "range": "last_6_months",
                "data": enriched_data,
            },
            status=status.HTTP_200_OK,
        )


# 탈퇴 사유 추이 막대 그래프
class AdminWithdrawalReasonTrendView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        responses={200: WithdrawalReasonTrendResponseSerializer},
        summary="탈퇴 사유 월별 추이 그래프 조회",
        description="최근 12개월간 특정 탈퇴 사유의 월별 발생 수를 조회하여 bar 또는 line 차트용 데이터로 반환합니다.",
        tags=["Admin - 유저 대시보드"],
        parameters=[
            OpenApiParameter(
                name="reason",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="탈퇴 사유: '비쌈' 또는 '불만족' 또는 '기타'",
            )
        ],
    )
    def get(self, request: Request) -> Response:
        reason_param = request.query_params.get("reason", Withdrawal.Reason.ETC.label)  # 기본값: 기타
        chart_type = request.query_params.get("chart_type", ChartTypeEnum.BAR.value)

        if chart_type not in [item.value for item in ChartTypeEnum]:
            return Response(
                {"detail": f"'{chart_type}'은(는) 유효하지 않은 차트 타입입니다. (bar 또는 line 중 하나)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # reason_param을 enum 값으로 역매핑
        label_to_value = {label: value for value, label in Withdrawal.Reason.choices}
        reason_value = label_to_value.get(reason_param)

        if not reason_value:
            return Response(
                {"detail": f"'{reason_param}'은(는) 유효한 탈퇴 사유가 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = datetime.today()
        start_date = (today.replace(day=1) - relativedelta(months=12)).date()

        # 집계 쿼리
        qs: List[Dict[str, Union[datetime, int]]] = list(
            Withdrawal.objects.filter(reason=reason_value, created_at__date__gte=start_date)
            .annotate(period=TruncMonth("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        # 라벨 생성
        labels = [(today.replace(day=1) - relativedelta(months=(11 - i))).strftime("%Y-%m") for i in range(13)]

        # 결과 정리
        raw_counts: Dict[str, int] = {}
        for item in qs:
            period = item["period"]
            if isinstance(period, datetime):
                key = period.strftime("%Y-%m")
            else:
                key = str(period)
            raw_counts[key] = cast(int, item["count"])

        data = OrderedDict((label, raw_counts.get(label, 0)) for label in labels)

        return Response(
            {
                "title": f"{reason_param} 탈퇴 사유 추이 {labels[0]} ~ {labels[-1]}",
                "graph_type": "withdraw_reason",
                "chart_type": chart_type,
                "range": "last_12_months",
                "reason": reason_param,
                "data": data,
            },
            status=status.HTTP_200_OK,
        )
