from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import datetime

from apps.tests.serializers.user_admin_deployment_serializers import CodeValidationRequestSerializer, DeploymentListSerializer


# MOCK 데이터 (변경 가능하도록 global 선언)
MOCK_DEPLOYMENTS = [
    {
        "deployment_id": 101,
        "test_title": "HTML 기초",
        "subject_title": "웹프로그래밍",
        "course_generation": "웹프로그래밍 5기",
        "total_participants": 15,
        "average_score": 85.6,
        "status": "Activated",
        "created_at": "2025-06-19T09:00:00"
    },
    {
        "deployment_id": 102,
        "test_title": "CSS 심화",
        "subject_title": "웹디자인",
        "course_generation": "웹디자인 4기",
        "total_participants": 10,
        "average_score": 78.2,
        "status": "Deactivated",
        "created_at": "2025-06-18T13:30:00"
    }
]

MOCK_DEPLOYMENTS_DETAILS = {
    101: {
        "test_id": 301, "test_name": "기초 Python 문법 테스트", "subject_name": "core", "question_count": 10,
        "deployment_id": 101, "test_url": "https://ozclass.com/tests/101", "access_code": "aB3dE9",
        "course_name": "오즈 인스턴십", "course_term": "1기", "duration_minutes": 60,
        "started_at": datetime(2025, 6, 24, 14, 0), "ended_at": datetime(2025, 6, 24, 15, 0),
        "status": "Activated", "created_at": datetime(2025, 6, 24, 9, 12), "updated_at": datetime(2025, 6, 24, 10, 0),
        "total_participants": 28, "absent_participants": 4
    },
    102: {
        "test_id": 302, "test_name": "자료 구조와 알고리즘 중급 테스트", "subject_name": "liew", "question_count": 15,
        "deployment_id": 102, "test_url": "https://ozclass.com/tests/102", "access_code": "Zk3Lp1",
        "course_name": "백엔드", "course_term": "10기", "duration_minutes": 90,
        "started_at": datetime(2025, 6, 24, 16, 0), "ended_at": datetime(2025, 6, 24, 17, 30),
        "status": "Activated", "created_at": datetime(2025, 6, 24, 9, 38), "updated_at": datetime(2025, 6, 24, 10, 30),
        "total_participants": 33, "absent_participants": 1
    }
}


def paginate_response(request, data, serializer_class):
    q = request.query_params
    s = q.get("search", "").lower()
    if s:
        data = [d for d in data if s in d["name"].lower() or s in d["subject_name"].lower()]
    ordering = q.get("ordering", "-created_at")
    reverse, key = ordering.startswith("-"), ordering.lstrip("-")
    if data and key in data[0]:
        data.sort(key=lambda x: x.get(key), reverse=reverse)

    paginator = PageNumberPagination()
    paginator.page_size = int(q.get("page_size", 10)) if q.get("page_size", "").isdigit() else 10
    page = paginator.paginate_queryset(data, request)
    return paginator.get_paginated_response(serializer_class(page, many=True).data)


@extend_schema(
    methods=["POST"],
    description="관리자용 참가코드 검증 MOCK API",
    request=CodeValidationRequestSerializer,
    responses={200: dict, 400: dict},
    tags=["test"],
)
class TestValidateCodeAdminView(APIView):
    def post(self, request):
        serializer = CodeValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        deployment_id = data["deployment_id"]
        access_code = data["access_code"]

        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)
        if details and details.get("access_code") == access_code and details.get("status") == "Activated":
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": details.get("test_name"),
                "deployment_id": deployment_id,
                "duration_time": details.get("duration_minutes", 60)
            })

        return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["PATCH"],
    parameters=[OpenApiParameter("deployment_id", int, OpenApiParameter.PATH)],
    responses={200: dict, 404: dict},
    description="쪽지시험 배포 상태 토글 MOCK API",
    tags=["test"],
)
class TestDeploymentStatusView(APIView):
    def patch(self, request, deployment_id):
        # MOCK_DEPLOYMENTS 리스트에서 해당 배포 찾기
        deployment = next((d for d in MOCK_DEPLOYMENTS if d["id"] == deployment_id), None)
        details = MOCK_DEPLOYMENTS_DETAILS.get(deployment_id)

        if not deployment or not details:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 상태 토글
        current_status = deployment["status"]
        new_status = "Deactivated" if current_status == "Activated" else "Activated"

        deployment["status"] = new_status
        details["status"] = new_status

        return Response({
            "deployment_id": deployment_id,
            "status": new_status,
            "message": "배포 상태가 성공적으로 변경되었습니다."
        })


@extend_schema(
    methods=["DELETE"],
    parameters=[OpenApiParameter("deployment_id", int, OpenApiParameter.PATH)],
    responses={204: None, 404: dict},
    description="쪽지시험 배포 삭제 MOCK API",
    tags=["test"],
)
class DeleteMiniTestDeploymentView(APIView):
    def delete(self, request, deployment_id):
        global MOCK_DEPLOYMENTS, MOCK_DEPLOYMENTS_DETAILS

        deployment_index = next((i for i, d in enumerate(MOCK_DEPLOYMENTS) if d["id"] == deployment_id), None)

        if deployment_index is None or deployment_id not in MOCK_DEPLOYMENTS_DETAILS:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 삭제 처리 (리스트/딕셔너리에서 삭제)
        del MOCK_DEPLOYMENTS[deployment_index]
        del MOCK_DEPLOYMENTS_DETAILS[deployment_id]

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter("search", str, required=False),
        OpenApiParameter("ordering", str, required=False),
        OpenApiParameter("page_size", int, required=False),
    ],
    tags=["test"],
)
class DeploymentListView(APIView):
    def get(self, request):
        return paginate_response(request, MOCK_DEPLOYMENTS, DeploymentListSerializer)

# 🔹 배포 내역 조회 API (