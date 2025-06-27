from typing import Any, Dict, List

from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import StudentEnrollmentRequest
from apps.users.serializers.admin_enrollments_serializers import (
    ApprovalResponseSerializer,
    EnrollmentRequestIdsSerializer,
)


class AdminApproveEnrollmentsView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ApprovalResponseSerializer

    @extend_schema(
        request=EnrollmentRequestIdsSerializer,
        responses={200: ApprovalResponseSerializer},
        summary="어드민 수강신청 일괄 승인",
        description="선택한 ID 중 'PENDING' 상태인 수강신청을 승인합니다.",
        tags=["Admin - 수강 신청"],
    )
    def post(self, request: Request) -> Response:
        serializer = EnrollmentRequestIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids: List[int] = serializer.validated_data["ids"]

        now = timezone.now()

        mock_enrollment: List[StudentEnrollmentRequest] = [
            StudentEnrollmentRequest(
                id=id_,
                user_id=0,
                generation_id=0,
                status=StudentEnrollmentRequest.EnrollmentStatus.APPROVED,
                accepted_at=now,
                created_at=now,
                updated_at=now,
            )
            for id_ in ids
        ]

        # 응답 메시지 및 serializer 구성
        message = f"{len(mock_enrollment)}건의 수강신청을 승인했습니다."
        response_data = {"approved_ids": [obj.id for obj in mock_enrollment], "message": message}

        response_serializer = ApprovalResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
