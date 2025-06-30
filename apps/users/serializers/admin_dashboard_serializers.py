from enum import Enum
from typing import Any

from rest_framework.serializers import (
    CharField,
    ChoiceField,
    FloatField,
    IntegerField,
    ListField,
    Serializer,
)


class ChartTypeEnum(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"


# 수강생 전환 추세 요청
class TrendQuerySerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["unit"] = ChoiceField(
            choices=["monthly", "yearly"],
            required=False,
            default="monthly",
            help_text="그래프 단위 (monthly | yearly)",
        )


# 수강생 전환 추세 응답
class ConversionTrendResponseSerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["title"] = CharField(help_text="그래프 제목 (예: 회원가입 추세 2024-01 ~ 2024-12)")
        self.fields["graph_type"] = CharField(help_text="그래프 종류 (예: student_conversion)")
        self.fields["chart_type"] = ChoiceField(
            choices=[e.value for e in ChartTypeEnum],
            help_text="차트 유형 (bar | line | pie | scatter)",
        )
        self.fields["range"] = CharField(help_text="조회 범위 설명 (예: last_12_months, last_4_years)")
        self.fields["labels"] = ListField(child=CharField(), help_text="X축 라벨 (월 또는 연도)")
        self.fields["data"] = ListField(child=IntegerField(), help_text="Y축 값 (수강생 전환 수)")


# 회원가입 추세 요청
class JoinTrendQuerySerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["range_type"] = ChoiceField(
            choices=["daily", "monthly", "yearly"],
            required=False,
            default="monthly",
            help_text="그래프 범위 단위 (daily | monthly | yearly)",
        )


# 회원가입 추세 응답
class JoinTrendResponseSerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["title"] = CharField(help_text="그래프 제목 (예: 회원가입 추세 2024-01 ~ 2024-12)")
        self.fields["graph_type"] = CharField(help_text="그래프 종류 (예: join)")
        self.fields["chart_type"] = ChoiceField(
            choices=[e.value for e in ChartTypeEnum],
            help_text="차트 유형 (bar | line | pie | scatter)",
        )
        self.fields["range_type"] = CharField(help_text="조회 범위 단위 (예: monthly)")
        self.fields["labels"] = ListField(child=CharField(), help_text="X축 라벨 (날짜, 월, 연도 등)")
        self.fields["data"] = ListField(child=IntegerField(), help_text="Y축 값 (해당 날짜의 회원가입 수)")


# 탈퇴 사유 개별 항목
class WithdrawalReasonStatSerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["reason"] = CharField(help_text="탈퇴 사유")
        self.fields["count"] = IntegerField(help_text="해당 사유로 탈퇴한 인원 수")
        self.fields["percentage"] = FloatField(help_text="비율 (%)")


# 탈퇴 사유 원형 그래프 응답
class WithdrawalReasonResponseSerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["title"] = CharField(help_text="그래프 제목 (예: 탈퇴 사유 비율 2024-01 ~ 2024-06)")
        self.fields["graph_type"] = CharField(help_text="그래프 유형 (예: withdraw_reason)")
        self.fields["chart_type"] = ChoiceField(
            choices=[e.value for e in ChartTypeEnum],
            help_text="차트 유형 (예: pie)",
        )
        self.fields["range"] = CharField(help_text="조회 범위 (예: last_6_months)")
        self.fields["data"] = WithdrawalReasonStatSerializer(many=True)


# 탈퇴 사유 추이 그래프 응답
class WithdrawalReasonTrendResponseSerializer(Serializer[Any]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["title"] = CharField(help_text="그래프 제목 (예: 탈퇴 사유 추이 2024-01 ~ 2024-12)")
        self.fields["graph_type"] = CharField(help_text="그래프 유형 (withdraw_reason)")
        self.fields["chart_type"] = ChoiceField(
            choices=[e.value for e in ChartTypeEnum],
            help_text="차트 유형 (bar | line)",
        )
        self.fields["range"] = CharField(help_text="조회 범위 (예: last_12_months)")
        self.fields["reason"] = CharField(help_text="조회 대상 탈퇴 사유")
        self.fields["labels"] = ListField(child=CharField(), help_text="X축 라벨 (월 단위)")
        self.fields["data"] = ListField(child=IntegerField(), help_text="Y축 데이터 값 (해당 월의 탈퇴 수)")
