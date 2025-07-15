from typing import Any, Optional

from django.db import transaction
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.core.utils.grading import get_questions_snapshot_from_deployment
from apps.tests.models import TestDeployment
from apps.tests.pagination import AdminTestListPagination
from apps.tests.permissions import IsAdminOrStaff
from apps.tests.serializers.test_deployment_serializers import (
    DeploymentCreateSerializer,
    DeploymentDetailSerializer,
    DeploymentListSerializer,
    DeploymentStatusUpdateSerializer,
)


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    request=DeploymentStatusUpdateSerializer,
    responses={200: dict, 404: dict},
    summary="배포 상태 변경",
    description="배포 아이디 기반으로 해당 상태를 PATCH 요청을 통해 활성화(Activated) 또는 비활성화(Deactivated)로 변경합니다. ",
)
# 배포 활성화/비활성화 토글 API
# PATCH 요청 시 해당 배포의 상태를 Activated ↔ Deactivated로 변경
class TestDeploymentStatusView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = DeploymentStatusUpdateSerializer

    def patch(self, request: Request, deployment_id: int) -> Response:
        try:
            deployment = TestDeployment.objects.get(id=deployment_id)
        except TestDeployment.DoesNotExist:
            return Response({"detail": "존재하지 않는 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=deployment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_deployment = serializer.save()

        return Response(
            {
                "deployment_id": updated_deployment.id,
                "status": updated_deployment.status,
                "message": "배포 상태가 성공적으로 변경되었습니다.",
                "updated_at": updated_deployment.updated_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer(many=True)},
    summary="쪽지시험 배포 목록 조회",
    description="시험 배포 ID 를 조회합니다. 페이징을 이용하여 조회합니다",
)
# 쪽지시험 배포 목록 조회
class DeploymentListView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = DeploymentListSerializer
    pagination_class = AdminTestListPagination

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 기본 쿼리셋 정의 및 N+1 문제 방지 (select_related)
        queryset = TestDeployment.objects.all().select_related(
            "test", "test__subject", "generation", "generation__course"
        )

        # 검색 (search)
        search_query: Optional[str] = request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                Q(test__title__icontains=search_query) | Q(test__subject__title__icontains=search_query)
            )

        # 필터링 (status)
        status_filter: Optional[str] = request.query_params.get("status", None)
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        # 필터링 (과정 - course_id, 기수 - generation_id) 로직
        raw_course_id: Optional[str] = request.query_params.get("course_id", None)
        raw_generation_id: Optional[str] = request.query_params.get("generation_id", None)

        if raw_course_id:
            try:
                parsed_course_id: int = int(raw_course_id)
                queryset = queryset.filter(generation__course__id=parsed_course_id)
            except ValueError:
                return Response(
                    {"detail": "course_id는 유효한 정수여야 합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if raw_generation_id:
            try:
                # 새로운 변수 parsed_generation_id에 정수형 값을 할당
                parsed_generation_id: int = int(raw_generation_id)
                queryset = queryset.filter(generation__id=parsed_generation_id)
            except ValueError:
                return Response(
                    {"detail": "generation_id는 유효한 정수여야 합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 이렇게 하면 집계 연산이 더 적은 수의 데이터에 대해 이루어져 효율적일 수 있습니다.
        queryset = queryset.annotate(
            total_participants=Count("submissions__student", distinct=True),
        )

        # 정렬 (ordering)
        ordering: Optional[str] = request.query_params.get("ordering", None)
        if ordering:
            valid_ordering_fields = [
                "total_participants",
                "created_at",
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
            queryset = queryset.order_by("-created_at")

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
    tags=["[Admin] Test - Deployment(쪽지시험 배포 생성/삭제/조회/활성화)"],
    responses={200: DeploymentListSerializer},
    summary="시험 배포 상세 조회",
    description=" 배포 ID에 해당하는 시험 배포의 상세 정보를 조회합니다. 미제출 인원 수 등 추가 데이터가 포함될 수 있습니다.",
)
# 쪽지시험 배포 상세 조회
class DeploymentDetailView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = DeploymentDetailSerializer

    def get(self, request: Request, deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            deployment = (
                TestDeployment.objects.select_related("test", "test__subject", "generation", "generation__course")
                .annotate(
                    # total_participants 계산: 해당 배포에 제출된 제출물의 학생 수를 카운트합니다.
                    total_participants=Count("submissions__student", distinct=True),
                    # total_generation_students 계산: 해당 기수(generation)의 전체 학생 수를 카운트합니다.
                    total_generation_students=Count("generation__students", distinct=True),
                )
                .get(pk=deployment_id)
            )
        except TestDeployment.DoesNotExist:
            return Response({"detail": "deployment_id가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        # 상세 시리얼라이저를 사용하여 객체를 JSON 형식으로 직렬화합니다.
        serializer = self.serializer_class(deployment, context={"request": request})

        # 직렬화된 데이터를 응답으로 반환합니다.
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    permission_classes = [IsAdminOrStaff]
    serializer_class = DeploymentCreateSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = DeploymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()를 호출하면 생성된 TestDeployment 인스턴스가 반환
        deployment = serializer.save()

        snapshot = get_questions_snapshot_from_deployment(deployment)
        deployment.question_count = len(snapshot)
        deployment.save(update_fields=["question_count"])

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

    permission_classes = [IsAdminOrStaff]
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
