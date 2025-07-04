from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.models import TestDeployment, TestSubmission
from apps.tests.permissions import IsStudent
from apps.tests.serializers.test_deployment_serializers import (
    UserTestDeploymentSerializer,
    UserTestStartSerializer,
)
from apps.tests.serializers.test_submission_serializers import (
    UserTestResultSerializer,
    UserTestSubmitSerializer,
)
from apps.users.models import PermissionsStudent


# 쪽지 시험 응시
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"],
    request=UserTestStartSerializer,
)
class TestStartView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    request_serializer_class = UserTestStartSerializer
    response_serializer_class = UserTestDeploymentSerializer

    def post(self, request: Request, test_id: int) -> Response:
        """
        쪽지 시험 응시 API
        """
        test_deployment = get_object_or_404(TestDeployment, test_id=test_id)
        now = timezone.now()

        # 배포 상태 확인
        if test_deployment.status != "Activated":
            return Response({"detail": "해당 시험은 현재 응시할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 시험 시작 시간 확인
        if test_deployment.open_at and test_deployment.open_at > now:
            return Response({"detail": "아직 응시할 수 없는 시험입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 시험 종료 시간 확인
        if test_deployment.close_at and test_deployment.close_at < now:
            return Response({"detail": "이미 종료된 시험입니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.request_serializer_class(
            data=request.data, context={"request": request, "test": test_deployment}
        )
        serializer.is_valid(raise_exception=True)

        response_serializer = self.response_serializer_class(instance=test_deployment)
        return Response(
            {"message": "시험 응시가 시작되었습니다.", "data": response_serializer.data}, status=status.HTTP_200_OK
        )


# 수강생 쪽지 시험 제출
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"],
    request=UserTestSubmitSerializer,
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
        serializer.save()

        # 자동 제출 메시지로 응답
        auto_msg = getattr(serializer, "auto_submit_message", None)
        if auto_msg:
            return Response({"detail": auto_msg}, status=200)

        return Response({"message": "시험 제출이 완료되었습니다."}, status=status.HTTP_200_OK)


# 쪽지 시험 결과 조회
@extend_schema(tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"])
class TestSubmissionResultView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserTestResultSerializer

    def get(self, request: Request, submission_id: int) -> Response:
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
