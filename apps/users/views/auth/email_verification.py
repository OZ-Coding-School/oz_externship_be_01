from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.email_verification import EmailVerificationSerializer


class EmailVerificationAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():

            return Response({"message": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
