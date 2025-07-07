from datetime import datetime
from http.client import responses
from typing import Any, Dict, List, Optional, cast
from uuid import uuid4

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment
from apps.tests.serializers.test_deployment_serializers import (
    DeploymentCreateSerializer,
    DeploymentDetailSerializer,
    DeploymentListSerializer,
    DeploymentStatusUpdateSerializer,
)

# 🔹 시험 데이터 (test.id 기준)
MOCK_TESTS: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "title": "HTML 기초", "subject": {"title": "웹프로그래밍"}},
    2: {"id": 2, "title": "CSS 심화", "subject": {"title": "웹디자인"}},
}
# 🔹 배포 데이터 (deployment.id 기준)
MOCK_GENERATIONS: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "5기", "course": {"id": 1, "title": "웹프로그래밍"}},
    2: {"id": 2, "name": "4기", "course": {"id": 2, "title": "웹디자인"}},
}


# 🔹 배포 데이터 (deployment.id 기준)
MOCK_DEPLOYMENTS: Dict[int, Dict[str, Any]] = {
    101: {
        "id": 101,
        "test": MOCK_TESTS[1],
        "generation": MOCK_GENERATIONS[1],
        "total_participants": 15,
        "average_score": 85.6,
        "duration_time": 60,
        "access_code": "aB3dE9",
        "status": "Activated",
        "open_at": datetime.now().isoformat(),
        "close_at": datetime.now().isoformat(),
        "questions_snapshot_json": {
            "1": {
                "question": "3 + 5 = ?",
                "choices": ["6", "7", "8"],
                "answer": "8",
            }
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    102: {
        "id": 102,
        "test": MOCK_TESTS[1],
        "generation": MOCK_GENERATIONS[2],
        "total_participants": 10,
        "average_score": 78.2,
        "duration_time": 90,
        "access_code": "fG7hJ2",
        "status": "Deactivated",
        "open_at": datetime.now().isoformat(),
        "close_at": datetime.now().isoformat(),
        "questions_snapshot_json": {
            "1": {
                "question": "CSS Flexbox의 주 용도는?",
                "choices": ["레이아웃", "애니메이션", "폼 제어"],
                "answer": "레이아웃",
            }
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
}


# @extend_schema(
#     tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
#     request=AdminCodeValidationSerializer,
#     responses={200: dict, 400: dict, 404: dict},
# )
# # 참가코드 검증( 어드민 )
# class TestValidateCodeAdminView(APIView):
#
#     permission_classes = [AllowAny]
#     serializer_class = AdminCodeValidationSerializer
#
#     def post(self, request: Request) -> Response:
#         serializer = AdminCodeValidationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         deployment_id = serializer.validated_data["deployment_id"]
#         access_code = serializer.validated_data["access_code"]
#
#         deployment: Optional[Dict[str, Any]] = MOCK_DEPLOYMENTS.get(deployment_id)
#         if not deployment:
#             return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)
#
#         if deployment["access_code"] == access_code and deployment["status"] == "Activated":
#             return Response(
#                 {
#                     "message": "참가코드가 유효합니다.",
#                     "test_title": deployment["test"]["title"],
#                     "deployment_id": deployment_id,
#                     "duration_time": deployment["duration_time"],
#                 }
#             )
#         return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["[MOCK/Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentStatusUpdateSerializer,
    responses={200: dict, 404: dict},
    summary="배포 상태 변경",
    description="배포 아이디 101.102 기반으로 해당 상태를 PATCH 요청을 통해 활성화(Activated) 또는 비활성화(Deactivated)로 변경합니다. ",
)
class TestDeploymentStatusView(APIView):

    # 배포 활성화/비활성화 토글 API
    # PATCH 요청 시 해당 배포의 상태를 Activated ↔ Deactivated로 변경

    permission_classes = [AllowAny]
    serializer_class = DeploymentStatusUpdateSerializer

    def patch(self, request: Request, deployment_id: int) -> Response:
        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeploymentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deployment["status"] = serializer.validated_data["status"]
        deployment["updated_at"] = str(datetime.now())

        return Response(
            {
                "deployment_id": deployment_id,
                "status": deployment["status"],
                "message": "배포 상태가 성공적으로 변경되었습니다.",
            }
        )


@extend_schema(
    tags=["[MOCK/Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer(many=True)},
    summary="시험 배포 목록 조회",
    description="등록된 모든 시험 배포 정보(ID 101,102)를 조회합니다. 페이징 없이 전체 데이터를 반환합니다.",
)
class DeploymentListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = DeploymentListSerializer

    def get(self, request: Request) -> Response:
        # dict.values()를 리스트로 변환
        deployments_list = list(MOCK_DEPLOYMENTS.values())
        serializer = DeploymentListSerializer(deployments_list, many=True)
        data = cast(List[Dict[str, Any]], serializer.data)
        return Response({"count": len(data), "next": None, "previous": None, "results": data})


@extend_schema(
    tags=["[MOCK/Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer},
    summary="시험 배포 상세 조회",
    description="지정한 배포 ID(101,102)에 해당하는 시험 배포의 상세 정보를 조회합니다. 미제출 인원 수 등 추가 데이터가 포함될 수 있습니다.",
)
class DeploymentDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = DeploymentDetailSerializer

    def get(self, request: Request, deployment_id: int) -> Response:
        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 예: 미제출 인원 수는 하드코딩 혹은 계산 필요
        deployment["unsubmitted_participants"] = 3  # 예시
        serializer = self.serializer_class(deployment)
        return Response(serializer.data)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentCreateSerializer,
    responses={201: dict},
    summary="시험 배포 생성",
    description=(
        "시험 ID(test_id (1)), 기수 ID(generation(1)), 시험 시간(duration_time (60))을 입력하여 새로운 시험 배포를 생성합니다."
        " 참가 코드(access_code)는 `uuid.uuid4().int` 값을 Base62 인코딩하여 정확히 6자리 무작위 문자열로 자동 생성되며, 문제 스냅샷이 포함됩니다."
    ),
)
# TestDeployment 배포 생성 API 뷰 클래스
class TestDeploymentCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = DeploymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()를 호출하면 생성된 TestDeployment 인스턴스가 반환
        deployment = serializer.save()
        # 응답 데이터
        responses_data = {
            "deployment_id": deployment.id,
            "access_code": deployment.access_code,
            "status": deployment.status,
        }
        return Response(responses_data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 삭제)"],
    summary="시험 배포 삭제",
    description="지정한 배포 I(101,102)D에 해당하는 시험 배포를 삭제합니다. 삭제 시 해당 배포 정보는 더 이상 조회할 수 없습니다.",
)
class TestDeploymentDeleteView(APIView):
    """
    배포 삭제 API
    DELETE 요청 시 특정 배포를 삭제
    """
    permission_classes = [IsAdminUser]
    serializer_class = DeploymentCreateSerializer

    def delete(self, request: Request, deployment_id: int, *args, **kwargs) -> Response:
        try:
            deployment = get_object_or_404(TestDeployment, id=deployment_id)
            # 데이터 무결성을 위한 트랜젝션 처리
            with transaction.atomic():
                deployment_title = deployment.test.title if deployment.test else "N/A Test"
                deployment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"detail": "배포 내역 삭제 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



