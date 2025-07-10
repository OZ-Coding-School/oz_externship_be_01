from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.auth.signup import (
    SignupNicknameCheckSerializer,
    SignUpSerializer,
)
from apps.users.utils.nickname_validators import is_nickname_duplicated
from rest_framework.parsers import MultiPartParser, FormParser
from apps.users.serializers.auth.signup import SignUpSerializer


class SignUpAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=SignUpSerializer, responses={201: None, 400: None}, tags=["auth"], summary="회원가입")
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupNicknameCheckAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SignupNicknameCheckSerializer,
        responses={200: None, 400: None},
        tags=["auth"],
        summary="닉네임 중복 확인 API",
    )
    def post(self, request):
        serializer = SignupNicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nickname = serializer.validated_data["nickname"]

        if is_nickname_duplicated(nickname):
            return Response({"message": "이미 사용 중인 닉네임입니다."}, status=400)

        return Response({"message": "사용 가능한 닉네임입니다."})
