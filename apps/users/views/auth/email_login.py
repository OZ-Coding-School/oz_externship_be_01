from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.users.serializers.auth.email_login import EmailLoginSerializer


class EmailLoginAPIView(APIView):
    @extend_schema(
        request=EmailLoginSerializer,
        responses={200: None, 400: None},
        tags=["auth"],)
    def post(self, request: Request) -> Response:
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "로그인 성공"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
