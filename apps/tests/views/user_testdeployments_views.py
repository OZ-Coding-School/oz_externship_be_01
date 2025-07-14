from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.core.utils.filters import (
    filter_deployments_by_course_and_generation,
    filter_deployments_by_submission_status,
)
from apps.tests.models import TestDeployment
from apps.tests.permissions import IsStudent
from apps.tests.serializers.test_deployment_serializers import (
    TestSubmissionListFilterSerializer,
    UserCodeValidationSerializer,
    UserTestDeploymentListSerializer,
)
from apps.users.models import PermissionsStudent


@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 참가코드 검증)"],
    request=UserCodeValidationSerializer,
    responses={200: dict, 400: dict, 404: dict},
    summary="쪽지시험 참가코드 검증 API",
    description="path, DB로 test_deployment_id를 받고, DB로 access_code만 받아 참가코드를 검증합니다.",
)
class UserCodeValidationView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserCodeValidationSerializer

    def post(self, request: Request, test_deployment_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            test_deployment = TestDeployment.objects.get(id=test_deployment_id)
        except TestDeployment.DoesNotExist:
            return Response(data={"detail": "존재하지 않는 시험 배포입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data, context={"test_deployment": test_deployment})
        serializer.is_valid(raise_exception=True)

        return Response({"detail": "참가코드가 유효합니다."}, status=status.HTTP_200_OK)


# 수강생 쪽지 시험 목록 조회
@extend_schema(
    tags=["[User] Test - Deployment (쪽지시험 목록조회)"],
    parameters=[
        OpenApiParameter(
            name="submission_status",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            enum=["completed", "not_submitted"],
            description="정렬 기준: 응시완료(submitted), 미응시(not_submitted)",
        ),
    ],
)
class TestDeploymentListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserTestDeploymentListSerializer

    def get(self, request: Request) -> Response:
        """
        쪽지 시험 목록 조회 API
        """
        student = get_object_or_404(PermissionsStudent, user=request.user)

        filter_serializer = TestSubmissionListFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        deployments = (
            TestDeployment.objects.filter(generation=student.generation)
            .select_related("test", "generation__course")
            .prefetch_related("submissions")
        )

        deployments = filter_deployments_by_course_and_generation(deployments, filters)
        deployments = filter_deployments_by_submission_status(deployments, student, filters.get("submission_status"))

        if not deployments.exists():
            msg = "시험 목록이 존재하지 않습니다."
            submission_status = filters.get("submission_status")
            if submission_status == "completed":
                msg = "응시한 시험이 없습니다."
            elif submission_status == "not_submitted":
                msg = "모든 시험에 응시하셨습니다."
            return Response({"detail": msg}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(deployments, many=True, context={"student": student})
        return Response(
            {"message": "쪽지시험 응시내역 목록 조회 완료", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
