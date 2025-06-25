from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.phone_verification import PhoneVerificationSerializer


class PhoneVerificationAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = PhoneVerificationSerializer(data=request.data)
        if serializer.is_valid():

            return Response({"message": "인증 코드가 휴대폰으로 전송되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
