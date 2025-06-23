from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response


@extend_schema(
    methods=["DELETE"],
    description="관리자 또는 스태프가 등록한 쪽지시험 문제를 Hard Delete 방식으로 삭제합니다.",
    responses={
        204: None,
        404: {"세부 정보 : 테스트 질문을 찾을 수 없습니다."}
    }
)