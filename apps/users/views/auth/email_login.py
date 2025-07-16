from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers.auth.email_login import (
    EmailLoginResponseSerializer,
    EmailLoginSerializer,
)


class EmailLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailLoginSerializer,
        responses={200: None, 401: None, 403: None},
        tags=["auth"],
        summary="이메일 로그인",
    )
    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    return Response({"detail": "탈퇴한 계정입니다."}, status=403)
                if not user.check_password(password):
                    return Response({"detail": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=401)

                refresh = RefreshToken.for_user(user)
                user_data = EmailLoginResponseSerializer(user).data

                # 이메일 로그인 시리얼라이저 생성후 직렬화
                return Response(
                    {
                        "message": "이메일 로그인에 성공했습니다.",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": user_data,
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response({"detail": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=401)
        return Response(serializer.errors, status=400)
