from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.student_enrollment_serializers import (
    EnrollmentRequestCreateSerializer,
)


class EnrollmentRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EnrollmentRequestCreateSerializer,
        responses={201: OpenApiTypes.OBJECT},
        tags=["수강신청"],
        summary="수강신청 생성",
        description="로그인한 유저가 특정 기수에 수강신청을 합니다. 이미 신청한 경우 중복 신청은 불가합니다.",
    )
    def post(self, request):
        serializer = EnrollmentRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "수강신청이 완료되었습니다."}, status=status.HTTP_201_CREATED)
