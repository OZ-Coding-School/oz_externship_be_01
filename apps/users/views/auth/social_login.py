from typing import Dict, Optional

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.auth.social_login import SocialLoginSerializer
from apps.users.utils.jwt import generate_jwt_token_pair
from apps.users.utils.social_auth import verify_kakao_token, verify_naver_token


class KakaoLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SocialLoginSerializer,
        responses={200: Dict[str, str], 400: Dict[str, str]},
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token: str = serializer.validated_data["access_token"]

        kakao_user_info: Optional[Dict[str, Optional[str]]] = verify_kakao_token(access_token)
        if kakao_user_info is None:
            return Response({"detail": "Invalid Kakao token."}, status=status.HTTP_400_BAD_REQUEST)

        email: Optional[str] = kakao_user_info.get("email")
        if email is None:
            return Response({"detail": "Kakao account email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": kakao_user_info.get("nickname") or "",
                "nickname": kakao_user_info.get("nickname") or "",
                "phone_number": "",
                "birthday": None,
            },
        )

        jwt_tokens: Dict[str, str] = generate_jwt_token_pair(user.id)
        return Response(jwt_tokens, status=status.HTTP_200_OK)


class NaverLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SocialLoginSerializer,
        responses={200: Dict[str, str], 400: Dict[str, str]},
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token: str = serializer.validated_data["access_token"]

        naver_user_info: Optional[Dict[str, Optional[str]]] = verify_naver_token(access_token)
        if naver_user_info is None:
            return Response({"detail": "Invalid Naver token."}, status=status.HTTP_400_BAD_REQUEST)

        email: Optional[str] = naver_user_info.get("email")
        if email is None:
            return Response({"detail": "Naver account email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": naver_user_info.get("nickname") or "",
                "nickname": naver_user_info.get("nickname") or "",
                "phone_number": "",
                "birthday": None,
            },
        )

        jwt_tokens: Dict[str, str] = generate_jwt_token_pair(user.id)
        return Response(jwt_tokens, status=status.HTTP_200_OK)
