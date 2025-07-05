from typing import Any, List

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff
from apps.users.models import PermissionsStudent, StudentEnrollmentRequest, User
from apps.users.serializers.admin_enrollments_serializers import (
    ApprovalResponseSerializer,
    EnrollmentRequestIdsSerializer,
)


class AdminApproveEnrollmentsView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = ApprovalResponseSerializer

    @extend_schema(
        request=EnrollmentRequestIdsSerializer,
        responses={200: ApprovalResponseSerializer},
        summary="어드민 수강신청 일괄 승인",
        description="""
        어드민 또는 스태프가 대기/반려 상태의 수강신청을 일괄 승인합니다.
        승인된 유저는 자동으로 Student 권한을 부여받습니다.
        """,
        tags=["Admin - 수강 신청"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = EnrollmentRequestIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids: List[int] = serializer.validated_data["ids"]

        # 승인할 ID가 없다면 에러 반환
        if not ids:
            return Response(
                {"detail": "승인할 수강신청 ID 목록이 비어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        # PENDING 또는 REJECTED 상태만 승인 대상으로 조회
        target_enrollments = StudentEnrollmentRequest.objects.select_related("user").filter(
            id__in=ids,
            status__in=[
                StudentEnrollmentRequest.EnrollmentStatus.PENDING,
                StudentEnrollmentRequest.EnrollmentStatus.REJECTED,
            ],
        )

        if not target_enrollments.exists():
            return Response(
                {"detail": "승인 가능한 수강신청이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_ids: List[int] = []

        for enrollment in target_enrollments:
            if enrollment.status == StudentEnrollmentRequest.EnrollmentStatus.APPROVED:
                continue  # 이미 승인된 신청은 무시

            enrollment.status = StudentEnrollmentRequest.EnrollmentStatus.APPROVED
            enrollment.accepted_at = now
            enrollment.updated_at = now
            enrollment.save(update_fields=["status", "accepted_at", "updated_at"])
            updated_ids.append(enrollment.id)

            user = enrollment.user
            if user.role == User.Role.GENERAL:
                user.role = User.Role.STUDENT
                user.save(update_fields=["role"])

            if not PermissionsStudent.objects.filter(user=user, generation=enrollment.generation).exists():
                PermissionsStudent.objects.create(user=user, generation=enrollment.generation)

        message = f"{len(updated_ids)}건의 수강신청을 승인했습니다."
        response_data = {
            "approved_ids": updated_ids,
            "message": message,
        }

        return Response(response_data, status=status.HTTP_200_OK)
