from typing import Dict, Optional, cast
from urllib.parse import urlparse

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import SocialUser, User
from apps.users.serializers.auth.social_login import SocialLoginSerializer
from apps.users.utils.jwt import generate_jwt_token_pair
from apps.users.utils.kakao import (
    format_full_birthday,
    generate_unique_nickname,
    get_kakao_access_token,
    get_kakao_user_info,
    normalize_phone_number,
)
from apps.users.utils.social_auth import (
    get_naver_access_token,
    verify_naver_token,
)


class SocialLoginRedirectUriMixin:
    def _get_redirect_uri(self, request: Request, provider: str) -> str:
        referer = request.META.get("HTTP_REFERER")
        origin = request.META.get("HTTP_ORIGIN")

        if referer:
            parsed = urlparse(referer)
            client_host = f"{parsed.scheme}://{parsed.netloc}"
        elif origin:
            parsed = urlparse(origin)
            client_host = f"{parsed.scheme}://{parsed.netloc}"
        else:
            raise APIException("요청에는 Origin 또는 Referer 헤더가 포함되어야 합니다.")

        return f"{client_host}/auth/callback/{provider}"


class KakaoLoginAPIView(APIView, SocialLoginRedirectUriMixin):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SocialLoginSerializer,
        responses={200: Dict[str, str], 400: Dict[str, str]},
        tags=["auth"],
    )
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        redirect_uri = self._get_redirect_uri(request, "kakao")
        # access_token 요청
        access_token, error = get_kakao_access_token(code, redirect_uri=redirect_uri)

        if not access_token:
            if "invalid_grant" in (error or ""):
                return Response({"detail": "잘못된 인가 코드입니다."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"detail": f"카카오 서버 오류: {error or '알 수 없는 오류'}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 사용자 정보 요청
        user_info = get_kakao_user_info(access_token)
        if not user_info or not user_info.get("email") or not user_info.get("kakao_id"):
            return Response(
                {"detail": "카카오 사용자 정보 요청 실패 또는 필수 정보 누락"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 사용자 정보 파싱
        kakao_id = user_info.get("kakao_id")
        email = user_info.get("email")
        raw_nickname = user_info.get("nickname") or (f"kakao_{email.split('@')[0]}" if email else None)
        nickname = generate_unique_nickname(raw_nickname)
        name = user_info.get("name")
        raw_phone_number = user_info.get("phone_number")
        phone_number = normalize_phone_number(raw_phone_number)
        birthday = format_full_birthday(user_info.get("birthyear"), user_info.get("birthday"))
        profile_image_url = user_info.get("profile_image_url")
        gender = user_info.get("gender")

        # 필수값 누락 여부 검사
        required_fields = {
            "kakao_id": kakao_id,
            "email": email,
            "nickname": nickname,
            "name": name,
            "phone_number": phone_number,
            "birthday": birthday,
            "gender": gender,
        }

        # 누락 필드 추출
        missing_fields = [field for field, value in required_fields.items() if not value]

        if missing_fields:
            return Response(
                {"detail": "잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 기존 소셜 유저 확인 또는 신규 생성
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(
                email=email,
                name=name,
                nickname=nickname,
                phone_number=phone_number,
                birthday=birthday,
                profile_image_url=profile_image_url,
                gender=gender,
            )

        SocialUser.objects.get_or_create(user=user, provider="KAKAO", provider_id=kakao_id)

        # JWT 발급
        tokens = generate_jwt_token_pair(user.id)
        return Response(tokens, status=status.HTTP_200_OK)


class NaverLoginAPIView(APIView, SocialLoginRedirectUriMixin):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SocialLoginSerializer,
        responses={200: Dict[str, str], 400: Dict[str, str]},
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code: str = serializer.validated_data["code"]
        state: Optional[str] = serializer.validated_data.get("state")
        redirect_uri = self._get_redirect_uri(request, "naver")

        # access token 발급
        access_token = get_naver_access_token(code, redirect_uri, state)
        if access_token is None:
            return Response({"detail": "네이버 토큰 발급에 실패했습니다. 잠시 후 다시 시도해주세요."}, status=400)

        # 사용자 정보 조회
        naver_user_info = verify_naver_token(access_token)
        if naver_user_info is None:
            return Response({"detail": "네이버 사용자 정보 조회에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 필수 정보 검증
        required_fields = ["email", "profile_image", "nickname", "name", "mobile", "birthyear", "birthday", "gender"]
        missing_fields = [field for field in required_fields if not naver_user_info.get(field)]
        if missing_fields:
            return Response(
                {"detail": f"필수 정보 누락: {', '.join(missing_fields)}. 네이버 제공 정보에 모두 동의해야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = naver_user_info.get("email")
        provider_id = naver_user_info.get("id")

        if not provider_id:
            return Response(
                {"detail": "네이버 서버의 일시적인 오류입니다. 잠시 후 다시 시도해주세요"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # 유저 생성 및 기본 유저 확인
        created = False

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            email = cast(str, naver_user_info.get("email"))
            name = cast(str, naver_user_info.get("name"))
            nickname = cast(str, naver_user_info.get("nickname"))
            phone_number = cast(str, naver_user_info.get("mobile"))

            user = User.objects.create(
                email=email,
                name=name,
                nickname=nickname,
                phone_number=phone_number,
                birthday=self._parse_birthday(naver_user_info),
                gender=self._parse_gender(naver_user_info.get("gender")),
            )
            created = True

        if not created:
            if not user.social_accounts.filter(provider=SocialUser.Provider.NAVER).exists():
                return Response(
                    {"detail": "이미 가입된 이메일입니다. 일반 로그인을 사용하거나 소셜 계정을 연동해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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

    def _parse_birthday(self, info: Dict[str, Optional[str]]) -> str:
        birthyear = info.get("birthyear")
        birthday = info.get("birthday")
        if birthyear and birthday:
            return f"{birthyear}-{birthday}"
        return ""

    def _parse_gender(self, gender: Optional[str]) -> str:
        if gender == "M":
            return User.Gender.MALE
        elif gender == "F":
            return User.Gender.FEMALE
        return ""
