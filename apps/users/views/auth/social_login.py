from typing import Dict, Optional

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import SocialUser, User
from apps.users.serializers.auth.social_login import SocialLoginSerializer
from apps.users.utils.jwt import generate_jwt_token_pair
from apps.users.utils.naver import verify_naver_token
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

        email = naver_user_info.get("email")
        provider_id = naver_user_info.get("id")

        if not email or not provider_id:
            return Response({"detail": "Naver account email and id are required."}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": naver_user_info.get("name") or "",
                "nickname": naver_user_info.get("nickname") or "",
                "phone_number": "",
                "birthday": None,
            },
        )

        # 기존 유저인데 네이버 연동 이력 없는 경우 예외 처리
        if not created:
            existing_social_user = user.social_accounts.filter(provider=SocialUser.Provider.NAVER).first()
            if not existing_social_user:
                return Response(
                    {"detail": "이미 가입된 이메일입니다. 일반 로그인을 사용하거나 소셜 계정을 연동해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # 소셜 유저 연결 정보 저장
        else:
            try:
                SocialUser.objects.create(
                    user=user,
                    provider=SocialUser.Provider.NAVER,
                    provider_id=provider_id,
                )
            except IntegrityError:
                return Response(
                    {"detail": "이미 등록된 네이버 계정입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        jwt_tokens: Dict[str, str] = generate_jwt_token_pair(user.id)
        return Response(jwt_tokens, status=status.HTTP_200_OK)
