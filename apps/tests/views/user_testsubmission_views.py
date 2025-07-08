from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    permission_classes = [IsAuthenticated]
    request_serializer_class = UserTestStartSerializer
    response_serializer_class = UserTestDeploymentSerializer

    def post(self, request: Request, test_id: int) -> Response:
        """
        이 API는 쪽지 시험 응시를 위한 test_id, access_code의 유효성을 판별합니다.
        """
        serializer = self.request_serializer_class(data=request.data, context={"test_id": test_id})
        serializer.is_valid(raise_exception=True)

        access_code = serializer.validated_data["access_code"]
        deployment = get_object_or_404(TestDeployment, access_code=access_code, test_id=test_id)

        response_serializer = self.response_serializer_class(instance=deployment)
        return Response(
            {"message": "Test started successfully.", "data": response_serializer.data}, status=status.HTTP_200_OK
        )


# 수강생 쪽지 시험 제출
@extend_schema(
    tags=["[User] Test - submission (쪽지시험 응시/제출/결과조회)"],
    request=UserTestSubmitSerializer,
)
class TestSubmissionSubmitView(APIView):
    # 실제 구현 시 수강생 권한 부여
    permission_classes = [AllowAny]
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
        test_submission = get_object_or_404(
            TestSubmission.objects.select_related("student", "deployment__test"), pk=submission_id
        )

        if test_submission.student.user != request.user:
            return Response({"detail": "본인만 결과조회가 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(instance=test_submission)
        return Response({"message": "쪽지시험 결과 조회 완료", "data": serializer.data}, status=status.HTTP_200_OK)
