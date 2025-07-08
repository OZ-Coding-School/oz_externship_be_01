from datetime import datetime
from typing import Any, Dict, List, Optional, cast
from uuid import uuid4

from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment
from apps.tests.pagination import AdminTestListPagination
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
    tags=["[Admin] Test - Deployment(쪽지시험 배포)"],
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
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer(many=True)},
    summary="쪽지시험 배포 목록 조회",
    description="시험 배포 ID 를 조회합니다. 페이징을 이용하여 조회합니다",
)

# 쪽지시험 배포 목록 조회
class DeploymentListView(APIView):

    permission_classes = [IsAdminUser]
    serializer_class = DeploymentListSerializer
    pagination_class = AdminTestListPagination

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 기본 쿼리셋 정의 및 N+1 문제 방지 (select_related)
        queryset = TestDeployment.objects.all().select_related(
            "test", "test__subject", "generation", "generation__course"  #  #  #  #
        )

        # total_participants 어노테이트(집계)
        queryset = queryset.annotate(
            total_participants=Count("submissions__student", distinct=True),  #
        )

        # 검색 (search)
        search_query: Optional[str] = request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                Q(test__title__icontains=search_query)  #
                | Q(test__subject__title__icontains=search_query)  #
                | Q(generation__course__name__icontains=search_query)  #
                | Q(generation__name__icontains=search_query)  #
            )

        # 필터링 (status)
        status_filter: Optional[str] = request.query_params.get("status", None)
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)  #

        # 정렬 (ordering)
        ordering: Optional[str] = request.query_params.get("ordering", None)
        if ordering:
            valid_ordering_fields = [
                "deployment_id",  #
                "test__title",  #
                "test__subject__title",  #
                "generation__course__name",  #
                "generation__number",  #
                "total_participants",
                "status",  #
                "created_at",  #
            ]
            if ordering.lstrip("-") in valid_ordering_fields:
                queryset = queryset.order_by(ordering)
            else:
                return Response(
                    {
                        "detail": f"유효하지 않은 정렬 필드입니다: {ordering}. 가능한 필드: {', '.join(valid_ordering_fields)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # 기본 정렬 (최신순)
            queryset = queryset.order_by("-created_at")  #

        # 페이지네이션 적용 (외부 페이지네이션 클래스 사용)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 페이지가 비어있을 경우 (페이지 번호가 범위를 벗어난 경우)
        if page is None:
            return paginator.get_paginated_response([])

        # 데이터 직렬화
        serializer = self.serializer_class(page, many=True)

        # 페이지네이션 응답 형식에 맞춰 반환
        return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["[MOCK/Admin] Test - Deployment(쪽지시험 배포/생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer},
    summary="시험 배포 상세 조회",
    description=" 배포 ID에 해당하는 시험 배포의 상세 정보를 조회합니다. 미제출 인원 수 등 추가 데이터가 포함될 수 있습니다.",
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
# 쪽지시험  배포 생성 API 뷰 클래스
class TestDeploymentCreateView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeploymentCreateSerializer

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
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    summary="시험 배포 삭제",
    description="test_id(deployment_id)룰 임력하여 시험 배포를 삭제합니다. 삭제 시 해당 배포 정보는 더 이상 조회할 수 없습니다.",
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
            # get_object_or_404 대신 TestDeployment.objects.get()을 직접 사용(객체가 없을 경우 TestDeployment.DoesNotExist 예외가 발생)
            deployment = TestDeployment.objects.get(id=deployment_id)
            # 데이터 무결성을 위한 트랜젝션 처리
            with transaction.atomic():
                deployment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except TestDeployment.DoesNotExist:
            # 배포가 존재하지 않는 경우 404 Not Found 응답 반환
            return Response({"detail": "존재하지 않는 배포입니다.."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # 그 외 모든 예외는 500 Internal Server Error 응답 반환
            return Response(
                {"detail": "배포 내역 삭제 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
