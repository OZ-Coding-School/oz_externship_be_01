from django.contrib.auth.models import AnonymousUser
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.profile_serializers import (
    NicknameCheckSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)


# 프로필 확인
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="(Mock) 내 정보 조회 API",
        tags=["profile"],
        responses={200: UserProfileSerializer},
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert not isinstance(user, AnonymousUser), "Authenticated user required"

        user_data = {
            "profile_image_url": user.profile_image_url or "https://dummyimage.com/100x100",
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "phone_number": user.phone_number,
            "birthday": user.birthday,
        }

        if user.role == User.Role.STUDENT:
            user_data.update(
                {
                    "course_name": "백앤드 개발",
                    "generation": "10기",
                }
            )

        return Response(user_data, status=status.HTTP_200_OK)


# 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=UserProfileUpdateSerializer,
        description="(Mock) 내 정보 수정 API",
        tags=["profile"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def put(self, request: Request) -> Response:
        user = request.user

        assert not isinstance(user, AnonymousUser), "인증된 사용자만 접근 가능합니다."

        serializer = UserProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        dummy_user = user
        dummy_user.nickname = validated.get("nickname", user.nickname)
        dummy_user.phone_number = validated.get("phone_number", user.phone_number)

        if "profile_image_file" in validated:
            dummy_user.profile_image_url = f"media/users/profile_images/{validated['profile_image_file']}"

        return Response(
            {
                "message": "더미 유저 정보 수정 완료",
                "updated_fields": {
                    "nickname": dummy_user.nickname,
                    "phone_number": dummy_user.phone_number,
                    "profile_image_url": dummy_user.profile_image_url,
                },
            },
            status=status.HTTP_200_OK,
        )


# 닉네임 중복 확인
class NicknameCheckView(APIView):
    @extend_schema(
        request=NicknameCheckSerializer,
        description="(Mock) 닉네임 중복 확인 API",
        tags=["profile"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request: Request) -> Response:
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)
