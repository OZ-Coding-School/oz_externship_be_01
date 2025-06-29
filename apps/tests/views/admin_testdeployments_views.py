from datetime import datetime
from uuid import uuid4
from typing import Dict, Any

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.tests.serializers.test_deployment_serializers import (
    AdminCodeValidationSerializer,
    DeploymentListSerializer,
    DeploymentCreateSerializer,
    DeploymentStatusUpdateSerializer,
)

# MOCK 데이터 (DB 대신 메모리 저장된 테스트 배포 데이터)
MOCK_DEPLOYMENTS: Dict[int, Dict[str, Any]] = {
    101: {
        "id": 101,
        "test": {"id": 1, "title": "Python 기초"},
        "generation": {"id": 1, "name": "1기", "course": {"id": 1, "title": "풀스택"}},
        "duration_time": 60,
        "access_code": "aB3dE9",
        "status": "Activated",
        "open_at": str(datetime.now()),
        "close_at": str(datetime.now()),
        "questions_snapshot_json": {},
        "created_at": str(datetime.now()),
        "updated_at": str(datetime.now()),
    }
}

@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=AdminCodeValidationSerializer,
    responses={200: dict, 400: dict, 404: dict},
)
# 참가코드 검증( 어드민 )
class TestValidateCodeAdminView(APIView):

    permission_classes = [AllowAny]
    serializer_class = AdminCodeValidationSerializer
    def post(self, request) -> Response:
        serializer = AdminCodeValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deployment_id = serializer.validated_data["deployment_id"]
        access_code = serializer.validated_data["access_code"]

        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        if deployment["access_code"] == access_code and deployment["status"] == "Activated":
            return Response({
                "message": "참가코드가 유효합니다.",
                "test_title": deployment["test"]["title"],
                "deployment_id": deployment_id,
                "duration_time": deployment["duration_time"],
            })
        return Response({"detail": "유효하지 않은 참가코드입니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentStatusUpdateSerializer,
    responses={200: dict, 404: dict},
)
class TestDeploymentStatusView(APIView):

    # 배포 활성화/비활성화 토글 API
    # PATCH 요청 시 해당 배포의 상태를 Activated ↔ Deactivated로 변경

    permission_classes = [AllowAny]
    serializer_class = DeploymentStatusUpdateSerializer
    def patch(self, request, deployment_id: int) -> Response:
        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeploymentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deployment["status"] = serializer.validated_data["status"]
        deployment["updated_at"] = str(datetime.now())

        return Response({
            "deployment_id": deployment_id,
            "status": deployment["status"],
            "message": "배포 상태가 성공적으로 변경되었습니다.",
        })


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer(many=True)},
)
class DeploymentListView(APIView):
    """
    배포 목록 조회 API
    - 저장된 모든 배포 정보를 리스트 형태로 반환
    """
    permission_classes = [AllowAny]
    serializer_class = DeploymentListSerializer
    def get(self, request) -> Response:
        return Response(DeploymentListSerializer(list(MOCK_DEPLOYMENTS.values()), many=True).data)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer},
)
class DeploymentDetailView(APIView):

    # 배포 상세 조회 API
    # 배포 ID에 해당하는 상세 정보를 반환

    permission_classes = [AllowAny]
    serializer_class = DeploymentListSerializer
    def get(self, request, deployment_id: int) -> Response:
        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DeploymentListSerializer(deployment).data)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentCreateSerializer,
    responses={201: DeploymentListSerializer},
)
class TestDeploymentCreateView(APIView):

    # 새로운 배포 생성 API
    # 클라이언트로부터 시험, 기수, 시간 등의 정보를 입력받아 배포 생성
    # 생성된 배포 정보를 반환

    permission_classes = [AllowAny]
    serializer_class = DeploymentCreateSerializer
    def post(self, request) -> Response:
        serializer = DeploymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        now = str(datetime.now())
        new_id = max(MOCK_DEPLOYMENTS.keys(), default=100) + 1

        # 새 배포 데이터 생성
        new_data = {
            "id": new_id,
            "test": {
                "id": validated["test"].id,
                "title": getattr(validated["test"], "title", "제목 없음"),
            },
            "generation": {
                "id": validated["generation"].id,
                "name": getattr(validated["generation"], "name", "기수 없음"),
                "course": {
                    "id": getattr(validated["generation"].course, "id", 0),
                    "title": getattr(validated["generation"].course, "title", "과정 없음"),
                },
            },
            "duration_time": validated.get("duration_time", 60),
            "access_code": str(uuid4())[:6],  # 6자리 무작위 참가코드 생성
            "status": "Activated",
            "open_at": validated.get("open_at", now),
            "close_at": validated.get("close_at", now),
            "questions_snapshot_json": {},
            "created_at": now,
            "updated_at": now,
        }

        MOCK_DEPLOYMENTS[new_id] = new_data

        return Response(DeploymentListSerializer(new_data).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화"],
)
class TestDeploymentDeleteView(APIView):

    # 배포 삭제 API
    #  DELETE 요청 시 특정 배포를 삭제

    permission_classes = [AllowAny]
    serializer_class = DeploymentCreateSerializer
    def delete(self, request, deployment_id: int) -> Response:
        if deployment_id not in MOCK_DEPLOYMENTS:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        del MOCK_DEPLOYMENTS[deployment_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
