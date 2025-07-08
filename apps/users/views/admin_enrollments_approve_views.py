from typing import List

from django.db import transaction
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
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = EnrollmentRequestIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids: List[int] = serializer.validated_data["ids"]

        updated_ids: List[int] = []

        with transaction.atomic():
            now = timezone.now()

            target_enrollments = (
                StudentEnrollmentRequest.objects.select_related("user", "generation")
                .select_for_update()
                .filter(
                    id__in=ids,
                    status__in=[
                        StudentEnrollmentRequest.EnrollmentStatus.PENDING,
                        StudentEnrollmentRequest.EnrollmentStatus.REJECTED,
                    ],
                )
            )

            if not target_enrollments.exists():
                return Response(
                    {"detail": "승인 가능한 수강신청이 존재하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for enrollment in target_enrollments:
                enrollment.status = StudentEnrollmentRequest.EnrollmentStatus.APPROVED
                enrollment.accepted_at = now
                enrollment.save(update_fields=["status", "accepted_at"])
                updated_ids.append(enrollment.id)

                user = enrollment.user
                if user.role == User.Role.GENERAL:
                    user.role = User.Role.STUDENT
                    user.save(update_fields=["role"])

                PermissionsStudent.objects.get_or_create(user=user, generation=enrollment.generation)

        response_data = {
            "approved_ids": updated_ids,
            "message": f"{len(updated_ids)}건의 수강신청을 승인했습니다.",
        }
        return Response(response_data, status=status.HTTP_200_OK)
