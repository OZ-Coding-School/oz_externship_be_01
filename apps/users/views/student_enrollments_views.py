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

    @extend_schema(request=EnrollmentRequestCreateSerializer, responses={201: None, 400: dict}, tags=["수강신청"])
    def post(self, request):
        serializer = EnrollmentRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
