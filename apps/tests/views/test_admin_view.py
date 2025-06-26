from datetime import datetime
from typing import Any, Optional


from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.tests.serializers.user_admin_deployment_serializers import (
    CodeValidationRequestSerializer,
    DeploymentCreateSerializer,
    DeploymentDetailSerializer,
    DeploymentListSerializer,
)

# MOCK 데이터 (변경 가능하도록 global 선언)
MOCK_DEPLOYMENTS : list[dict[str, Any]] = [
    {
        "deployment_id": 101,
        "test_title": "HTML 기초",
        "subject_title": "웹프로그래밍",
        "course_generation": "웹프로그래밍 5기",
        "total_participants": 15,
        "average_score": 85.6,
        "status": "Activated",
        "created_at": "2025-06-19T09:00:00",
    },
    {
        "deployment_id": 102,
        "test_title": "CSS 심화",
        "subject_title": "웹디자인",
        "course_generation": "웹디자인 4기",
        "total_participants": 10,
        "average_score": 78.2,
        "status": "Deactivated",
        "created_at": "2025-06-18T13:30:00",
    },
]

MOCK_DEPLOYMENTS_DETAILS: dict[int, dict[str, Any]] = {
    101: {
        "test": {"test_id": 101, "test_title": "HTML 기초", "subject_title": "웹프로그래밍", "question_count": 10},
        "deployment": {
            "deployment_id": 101,
            "access_url": "https://ozclass.com/exam/101",
            "access_code": "aB3dE9",
            "course_title": "웹프로그래밍 올인원 과정",
            "generation_title": "5기",
            "duration_time": 60,
            "open_at": "2025-06-19T09:00:00",
            "close_at": "2025-06-19T10:00:00",
            "status": "Activated",
            "created_at": "2025-06-18T12:00:00",
            "updated_at": "2025-06-18T18:30:00",
        },
        "submission_stats": {"total_participants": 15, "not_participated": 2},
    },
    102: {
        "test": {"test_id": 102, "test_title": "CSS 심화", "subject_title": "웹디자인", "question_count": 8},
        "deployment": {
            "deployment_id": 102,
            "access_url": "https://ozclass.com/exam/102",
            "access_code": "Zx81Lm",
            "course_title": "웹디자인 포트폴리오 캠프",
            "generation_title": "4기",
            "duration_time": 45,
            "open_at": "2025-06-18T13:30:00",
            "close_at": "2025-06-18T14:15:00",
            "status": "Deactivated",
            "created_at": "2025-06-17T10:00:00",
            "updated_at": "2025-06-17T16:45:00",
        },
        "submission_stats": {"total_participants": 10, "not_participated": 1},
    },
}


# 공용 함수
def paginate_response(request: Request, data: list[dict[str, Any]], serializer_class: type) -> Response:
    q = request.query_params
    s = q.get("search", "").lower()
    if s:
        data = [d for d in data if s in d["test_title"].lower() or s in d["subject_title"].lower()]
    ordering = q.get("ordering", "-created_at")
    reverse, key = ordering.startswith("-"), ordering.lstrip("-")
    if data and key in data[0]:
        data.sort(key=lambda x: x.get(key, ""), reverse=reverse)
    paginator = PageNumberPagination()
    paginator.page_size = int(q.get("page_size", 10)) if q.get("page_size", "").isdigit() else 10
    page: Optional[list[dict[str, Any]]] = paginator.paginate_queryset(data, request)  # type: ignore[arg-type]
    return paginator.get_paginated_response(serializer_class(page, many=True).data)


@extend_schema()
class TestValidateCodeAdminView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CodeValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        deployment_id = data["deployment_id"]
        access_code = data["access_code"]

        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)

        if (
            details
            and details["deployment"]["access_code"] == access_code
            and details["deployment"]["status"] == "Activated"
        ):
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": details["test"]["test_title"],
                "deployment_id": deployment_id,
                "duration_time": details["deployment"]["duration_time"],
            })

        return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
class TestDeploymentStatusView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request: Request, deployment_id: int) -> Response:
        deployment = next((d for d in MOCK_DEPLOYMENTS if d["deployment_id"] == deployment_id), None)
        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)

        if not deployment or not details:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        current_status = deployment["status"]
        new_status = "Deactivated" if current_status == "Activated" else "Activated"

        deployment["status"] = new_status
        details["status"] = new_status

        return Response({
            "deployment_id": deployment_id,
            "status": new_status,
            "message": "배포 상태가 성공적으로 변경되었습니다."
        })


@extend_schema()
class TestDeploymentCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = DeploymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"deployment_id": 123, "access_code": "Ab12CD", "status": "Activated"},
            status=status.HTTP_201_CREATED
        )


@extend_schema()
class DeleteMiniTestDeploymentView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request: Request, deployment_id: int) -> Response:
        global MOCK_DEPLOYMENTS, MOCK_DEPLOYMENTS_DETAILS

        deployment_index = next(
            (i for i, d in enumerate(MOCK_DEPLOYMENTS) if d["deployment_id"] == deployment_id), None
        )

        if deployment_index is None or deployment_id not in MOCK_DEPLOYMENTS_DETAILS:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        del MOCK_DEPLOYMENTS[deployment_index]
        del MOCK_DEPLOYMENTS_DETAILS[deployment_id]

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema()
class DeploymentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return paginate_response(request, MOCK_DEPLOYMENTS, DeploymentListSerializer)


@extend_schema()
class DeploymentDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, deployment_id: int) -> Response:
        raw_data = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)
        if not raw_data:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeploymentDetailSerializer(instance=raw_data)
        return Response(serializer.data)