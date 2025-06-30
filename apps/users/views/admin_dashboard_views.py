from datetime import date, timedelta
from typing import Callable, Dict, List, TypedDict, Union

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin_dashboard_serializers import (
    ChartTypeEnum,
    ConversionTrendResponseSerializer,
    JoinTrendQuerySerializer,
    JoinTrendResponseSerializer,
    TrendQuerySerializer,
    WithdrawalReasonResponseSerializer,
    WithdrawalReasonTrendResponseSerializer,
)


class AdminEnrollmentTrendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=TrendQuerySerializer,
        responses={200: ConversionTrendResponseSerializer},
        summary="수강생 전환 추세 조회",
        description="월별 또는 년별 단위로 수강생 전환 수를 그래프 데이터 형태로 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        serializer = TrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data["unit"]

        if unit == "monthly":
            labels = [f"2024-{m:02}" for m in range(1, 13)]
            data = [3, 5, 7, 2, 6, 4, 5, 6, 4, 3, 7, 8]
            range_ = "last_12_months"
        else:
            labels = ["2021", "2022", "2023", "2024"]
            data = [31, 45, 39, 50]
            range_ = "last_4_years"

        return Response(
            {
                "title": f"수강생 전환 추세 {labels[0]} ~ {labels[-1]}",
                "graph_type": "student_conversion",
                "chart_type": ChartTypeEnum.BAR.value,
                "range": range_,
                "data": dict(zip(labels, data)),
            },
            status=status.HTTP_200_OK,
        )


class AdminJoinTrendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=JoinTrendQuerySerializer,
        responses={200: JoinTrendResponseSerializer},
        summary="회원가입 추세 그래프 데이터 조회",
        description="일별/월별/연도별 회원가입 수를 조회합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        serializer = JoinTrendQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        range_type = serializer.validated_data["range_type"]

        label_generators: Dict[str, Callable[[], List[str]]] = {
            "daily": lambda: [(date(2025, 5, 21) + timedelta(days=i)).isoformat() for i in range(30)],
            "monthly": lambda: [
                f"{y}-{m:02}" for y in [2024, 2025] for m in (range(7, 13) if y == 2024 else range(1, 7))
            ],
            "yearly": lambda: [str(y) for y in range(2020, 2025)],
        }

        labels = label_generators[range_type]()
        data = [(i * 3 % 10) + 1 for i in range(len(labels))]

        return Response(
            {
                "title": f"회원가입 추세 {labels[0]} ~ {labels[-1]}",
                "graph_type": "join",
                "chart_type": ChartTypeEnum.BAR.value,
                "range": range_type,
                "data": dict(zip(labels, data)),
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
