from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.signup import SignupSerializer


class SignupAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():

            return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
