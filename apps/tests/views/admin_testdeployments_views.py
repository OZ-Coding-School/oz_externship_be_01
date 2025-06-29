from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.tests.serializers.test_deployment_serializers import (
    AdminCodeValidationSerializer,
    DeploymentListSerializer,
    DeploymentCreateSerializer,
    DeploymentStatusUpdateSerializer,
)

## 🔹 시험 데이터 (test.id 기준)
MOCK_TESTS = {
    1: {"id": 1, "title": "HTML 기초", "subject": {"title": "웹프로그래밍"}},
    2: {"id": 2, "title": "CSS 심화", "subject": {"title": "웹디자인"}},
}
# 🔹 배포 데이터 (deployment.id 기준)
MOCK_GENERATIONS = {
    1: {
        "id": 1,
        "name": "5기",
        "course": {
            "id": 1,
            "title": "웹프로그래밍"
        }
    },
    2: {
        "id": 2,
        "name": "4기",
        "course": {
            "id": 2,
            "title": "웹디자인"
        }
    }
}


# 🔹 배포 데이터 (deployment.id 기준)
MOCK_DEPLOYMENTS = {
    101: {
        "id": 101,
        "test": MOCK_TESTS[1],
        "generation": MOCK_GENERATIONS[1],
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
        "test": MOCK_TESTS[2],
        "generation": MOCK_GENERATIONS[2],
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
    permission_classes = [AllowAny]
    serializer_class = DeploymentListSerializer

    def get(self, request: Request) -> Response:
        # dict.values()를 리스트로 변환
        deployments_list = list(MOCK_DEPLOYMENTS.values())
        serializer = DeploymentListSerializer(deployments_list, many=True)
        data: List[Dict[str, Any]] = serializer.data
        return Response({
            "count": len(data),
            "next": None,
            "previous": None,
            "results": data
        })


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer},
)
class DeploymentDetailView(APIView):
    # 배포 상세 조회 API: 배포 ID로 상세 정보 반환
    permission_classes = [AllowAny]
    serializer_class = DeploymentListSerializer

    def get(self, request: Any, deployment_id: int) -> Response:
        deployment = MOCK_DEPLOYMENTS.get(deployment_id)
        if not deployment:
            return Response(
                {"detail": "존재하지 않는 배포입니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.serializer_class(deployment)
        return Response(serializer.data)

@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentCreateSerializer,
    responses={201: dict},
)
# TestDeployment 배포 생성 API 뷰 클래스
class TestDeploymentCreateView(APIView):

    permission_classes = [AllowAny]  # 권한 설정: 누구나 접근 가능
    serializer_class = DeploymentCreateSerializer  # 입력 검증용 시리얼라이저

        # POST 요청 처리: 배포 생성
    def post(self, request) -> Response:
        serializer = self.serializer_class(data=request.data)  # 요청 데이터 시리얼라이즈
        serializer.is_valid(raise_exception=True)  # 유효성 검사, 실패 시 예외 발생
        validated: Dict[str, Any] = serializer.validated_data  # 검증된 데이터

        test_id: int = validated["test"]  # 시험 ID
        generation_id: int = validated["generation"]  # 기수 ID

        # MOCK 데이터에서 시험, 기수 정보 조회
        test_info: Dict[str, Any] = MOCK_TESTS.get(test_id)  # 시험 정보 조회
        generation_info: Dict[str, Any] = MOCK_GENERATIONS.get(generation_id)  # 기수 정보 조회

        if not test_info:
            return Response({"detail": "존재하지 않는 시험입니다."}, status=status.HTTP_400_BAD_REQUEST)
        if not generation_info:
            return Response({"detail": "존재하지 않는 기수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        now: str = datetime.now().isoformat()  # 현재 시간 ISO 포맷 문자열
        new_id: int = max(MOCK_DEPLOYMENTS.keys(), default=100) + 1  # 새로운 배포 ID 생성

        new_data: Dict[str, Any] = {
            "id": new_id,  # 배포 ID
            "test": test_info,  # 시험 정보
            "generation": generation_info,  # 기수 정보
            "duration_time": validated.get("duration_time", 60),  # 시험 시간 (기본 60분)
            "access_code": str(uuid4())[:6],  # 6자리 무작위 참가코드 생성
            "status": "Activated",  # 상태
            "open_at": validated.get("open_at", now),  # 개시 시간
            "close_at": validated.get("close_at", now),  # 종료 시간
            "questions_snapshot_json": {  # 문제 스냅샷 예시
                "1": {
                    "question": "3 + 5 = ?",
                    "choices": ["6", "7", "8"],
                    "answer": "8",
                }
            },
            "created_at": now,  # 생성 시간
            "updated_at": now,  # 수정 시간
        }

        MOCK_DEPLOYMENTS[new_id] = new_data  # 메모리 저장

        response_data: Dict[str, Any] = {
            "deployment_id": new_data["id"],  # 응답용 배포 ID
            "access_code": new_data["access_code"],  # 응답용 참가 코드
            "status": new_data["status"],  # 응답용 상태
            "snapshot": new_data["questions_snapshot_json"],  # 응답용 문제 스냅샷
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

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
