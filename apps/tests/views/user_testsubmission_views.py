from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
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
from apps.tests.core.utils.grading import (
    calculate_correct_count,
    calculate_total_score,
    get_questions_snapshot_from_submission,
    validate_answers_json_format,
)
from apps.tests.models import TestDeployment, TestSubmission
from apps.tests.permissions import IsStudent
from apps.tests.serializers.test_deployment_serializers import (
    TestSubmissionListFilterSerializer,
    UserTestDeploymentListSerializer,
    UserTestDeploymentSerializer,
    UserTestStartSerializer,
)
from apps.tests.serializers.test_submission_serializers import (
    UserTestResultSerializer,
    UserTestSubmitSerializer,
)
from apps.users.models import PermissionsStudent


# 수강생 쪽지 시험 응시
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/목록/결과)"],
    request=UserTestStartSerializer,
)
class TestStartView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    request_serializer_class = UserTestStartSerializer
    response_serializer_class = UserTestDeploymentSerializer

    def post(self, request: Request, test_deployment_id: int) -> Response:
        """
        쪽지 시험 응시 API
        """
        test_deployment = get_object_or_404(TestDeployment, pk=test_deployment_id)
        now = timezone.now()

        # 배포 상태 확인
        if test_deployment.status != TestDeployment.TestStatus.ACTIVATED:
            return Response({"detail": "해당 시험은 현재 응시할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 시험 시작 시간 확인
        if test_deployment.open_at and test_deployment.open_at > now:
            return Response({"detail": "아직 응시할 수 없는 시험입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 시험 종료 시간 확인
        if test_deployment.close_at and test_deployment.close_at < now:
            return Response({"detail": "이미 종료된 시험입니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.request_serializer_class(data=request.data, context={"test_deployment": test_deployment})
        serializer.is_valid(raise_exception=True)

        response_serializer = self.response_serializer_class(instance=test_deployment)
        return Response(
            {"message": "시험 응시가 시작되었습니다.", "data": response_serializer.data}, status=status.HTTP_200_OK
        )


# 수강생 쪽지 시험 제출
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/목록/결과)"],
    request=UserTestSubmitSerializer,
    examples=[
        OpenApiExample(
            name="쪽지시험 제출 예시",
            value={
                "student": 1,
                "started_at": "2025-07-11T13:30:09.042Z",
                "cheating_count": 1,
                "answers_json": {
                    "1": ["A"],
                    "2": ["x"],
                    "3": ["<html>", "<head>", "<body>", "<title>"],
                    "4": ["title"],
                    "5": ["<title>", "<head>"],
                    "6": ["A", "B"],
                },
            },
            request_only=True,
        )
    ],
)
class TestSubmissionSubmitView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserTestSubmitSerializer

    def post(self, request: Request, deployment_id: int) -> Response:
        """
        쪽지 시험 제출 API
        """
        deployment = get_object_or_404(TestDeployment, id=deployment_id)
        student = get_object_or_404(PermissionsStudent, user=request.user)

        serializer = self.serializer_class(
            data=request.data,
            context={
                "request": request,
                "deployment": deployment,
                "student": student,
            },
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        snapshot = get_questions_snapshot_from_submission(submission)
        validate_answers_json_format(submission.answers_json, snapshot)

        submission.score = calculate_total_score(submission.answers_json, snapshot)
        submission.correct_count = calculate_correct_count(submission.answers_json, snapshot)
        submission.save(update_fields=["score", "correct_count"])

        # 자동 제출 메시지로 응답
        auto_msg = getattr(serializer, "auto_submit_message", None)
        if auto_msg:
            return Response({"detail": auto_msg}, status=200)

        return Response({"message": "시험 제출이 완료되었습니다."}, status=status.HTTP_200_OK)


# 수강생 쪽지 시험 목록 조회
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/목록/결과)"],
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
class TestSubmissionListView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated, IsStudent]
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


# 수강생 쪽지 시험 결과 조회
@extend_schema(tags=["[User] Test - submission (쪽지시험 응시/제출/목록/결과)"])
class TestSubmissionResultView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserTestResultSerializer

    def get(self, request: Request, submission_id: int) -> Response:
        """
        쪽지 시험 결과 조회 API
        """
        try:
            test_submission = TestSubmission.objects.select_related("student", "deployment__test").get(pk=submission_id)
        except TestSubmission.DoesNotExist:
            return Response(
                {"detail": f"{submission_id}에 해당하는 객체가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        if test_submission.student.user != request.user:
            return Response({"detail": "본인만 결과조회가 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(instance=test_submission)
        return Response({"message": "쪽지시험 결과 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)
