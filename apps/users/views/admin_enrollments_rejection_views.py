from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import PermissionsStudent, StudentEnrollmentRequest, User
from apps.users.serializers.admin_enrollments_rejection_serializers import (
    RejectEnrollmentRequestSerializer,
    RejectionResponseSerializer,
)

# pending, approved 상태만 반려
# rejected 상태이면 스킵
# approved 상태였는데 반려시킨거면 수강생 권한 general로 롤백, 권한삭제처리


class RejectEnrollmentRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RejectEnrollmentRequestSerializer,
        description="(Mock) 수강생 등록 신청 반려 API - 승인/대기 상태만 반려, 이미 반려된 항목 제외",
        tags=["Admin - 수강생 등록 신청 반려"],
        responses={200: RejectionResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = RejectEnrollmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["enrollment_request_ids"]

        rejected_ids = []
        skipped_ids = []
        downgraded_user_ids = []
        deleted_permission_ids = []
        status_enum = StudentEnrollmentRequest.EnrollmentStatus

        with transaction.atomic():
            enrollments = StudentEnrollmentRequest.objects.select_related("user", "generation").filter(id__in=ids)

            for enrollment in enrollments:

                if enrollment.status == status_enum.REJECTED:
                    skipped_ids.append(enrollment.id)
                    continue

                if enrollment.status == status_enum.APPROVED:
                    permissions = PermissionsStudent.objects.filter(user=enrollment.user, generation=enrollment.generation)
                    deleted_count = permissions.count()
                    deleted_permission_ids.extend([enrollment.user.id] * deleted_count)
                    permissions.delete()

                    if enrollment.user.role != User.Role.GENERAL:
                        enrollment.user.role = User.Role.GENERAL
                        enrollment.user.save(update_fields=["role"])
                        downgraded_user_ids.append(enrollment.user.id)

                enrollment.status = status_enum.REJECTED
                enrollment.save(update_fields=["status"])
                rejected_ids.append(enrollment.id)

        response_data = {
            "rejected_ids": rejected_ids,
            "skipped_ids": skipped_ids,
            "downgraded_user_ids": downgraded_user_ids,
            "deleted_permission_ids": deleted_permission_ids,
            "message": f"{len(rejected_ids)}건 반려 완료. {len(skipped_ids)}건 제외됨.",
        }

        return Response(RejectionResponseSerializer(response_data).data, status=status.HTTP_200_OK)
