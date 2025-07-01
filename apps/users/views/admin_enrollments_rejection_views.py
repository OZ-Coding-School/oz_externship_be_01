from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin_enrollments_rejection_serializers import (
    RejectEnrollmentRequestSerializer,
    RejectionResponseSerializer,
)


class RejectEnrollmentRequestView(APIView):
    permission_classes = [AllowAny]

    # pending, approved 상태만 반려
    # rejected 상태이면 스킵
    # approved 상태였는데 반려시킨거면 수강생 권한 general로 롤백, 권한삭제처리

    @extend_schema(
        request=RejectEnrollmentRequestSerializer,
        description="(Mock) 수강생 등록 신청 반려 API - 승인/대기 상태만 반려, 이미 반려된 항목 제외",
        tags=["Admin - 수강생 등록 신청 반려"],
        responses={200: RejectionResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = RejectEnrollmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollments = serializer.validated_data["enrollments"]

        rejected_ids = []
        skipped_ids = []
        downgraded_user_ids = []
        deleted_permission_ids = []

        for enrollment in enrollments:
            enrollment_id = enrollment["id"]
            status_value = enrollment["status"]

            if status_value == "REJECTED":
                skipped_ids.append(enrollment_id)
            elif status_value == "PENDING":
                rejected_ids.append(enrollment_id)
            elif status_value == "APPROVED":
                rejected_ids.append(enrollment_id)
                downgraded_user_ids.append(enrollment_id)
                deleted_permission_ids.append(enrollment_id)

        message = f"{len(rejected_ids)}건 반려 완료. {len(skipped_ids)}건은 이미 반려된 상태입니다."

        response_data = {
            "message": message,
            "rejected_ids": rejected_ids,
            "skipped_ids": skipped_ids,
            "downgraded_user_ids": downgraded_user_ids,
            "deleted_permission_ids": deleted_permission_ids,
            "mock_processed_at": datetime.now(),
        }

        response_serializer = RejectionResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
