from datetime import date, timedelta
from typing import Any, Callable, Dict, List, Union

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin_dashboard_serializers import (
    ConversionTrendResponseSerializer,
    JoinTrendQuerySerializer,
    JoinTrendResponseSerializer,
    TrendQuerySerializer,
    WithdrawalReasonResponseSerializer,
    WithdrawalReasonTrendResponseSerializer,
)


# 수강생 전환 추세 그래프
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
            labels = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
            data = [3, 5, 7, 2, 6, 4]
            range_ = "last_12_months"
        else:
            labels = ["2021", "2022", "2023", "2024"]
            data = [31, 45, 39, 50]
            range_ = "last_4_years"

        response_data: Dict[str, Any] = {
            "graph_type": "student_conversion",
            "range": range_,
            "labels": labels,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# 회원가입 추세 그래프
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

        labels: List[str] = label_generators[range_type]()
        data: List[int] = [(i * 3 % 10) + 1 for i in range(len(labels))]

        return Response(
            {"graph_type": "join", "range_type": range_type, "labels": labels, "data": data}, status=status.HTTP_200_OK
        )


# 회원 탈퇴 추세 그래프
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
        else:  # yearly
            labels = [str(y) for y in range(2021, 2025)]
            data = [10, 13, 8, 15]
            range_ = "last_4_years"

        response_data: Dict[str, Any] = {
            "graph_type": "withdraw",
            "range_type": unit,
            "labels": labels,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# 최근 6개월 내 탈퇴 사유 그래프 (원형)
class AdminWithdrawalReasonPieView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: WithdrawalReasonResponseSerializer},
        summary="회원 탈퇴 사유 통계 조회",
        description="최근 6개월 내 탈퇴 사유를 집계하여 원형 차트용 데이터를 반환합니다.",
        tags=["Admin - 유저 대시보드"],
    )
    def get(self, request: Request) -> Response:
        raw_data: List[Dict[str, Union[str, int]]] = [
            {"reason": "콘텐츠 불만족", "count": 12},
            {"reason": "가격 문제", "count": 10},
            {"reason": "기타", "count": 8},
        ]

        total: int = sum(item["count"] for item in raw_data if isinstance(item["count"], int))

        enriched_data: List[Dict[str, Union[str, int, float]]] = [
            {**item, "percentage": round(int(item["count"]) / total * 100, 1)} for item in raw_data
        ]

        response_data: Dict[str, Union[str, List[Dict[str, Union[str, int, float]]]]] = {
            "graph_type": "withdraw_reason",
            "chart_type": "pie",
            "range": "last_6_months",
            "data": enriched_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# 최근 12개월 내 탈퇴 사유 그래프 (막대 / 꺾은선)
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
        chart_type = request.query_params.get("chart_type", "bar")

        # 최근 12개월 생성 (2024-07 ~ 2025-06)
        labels = [f"2024-{m:02}" for m in range(7, 13)] + [f"2025-{m:02}" for m in range(1, 7)]
        data = [(i * 2 + 1) % 5 for i in range(12)]  # mock 숫자

        response_data = {
            "graph_type": "withdraw_reason",
            "chart_type": chart_type,
            "range": "last_12_months",
            "reason": reason,
            "labels": labels,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
