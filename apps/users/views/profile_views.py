from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
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
    permission_classes = [AllowAny]

    @extend_schema(
        description="(Mock) 내 정보 조회 API",
        tags=["profile"],
        responses={200: UserProfileSerializer},
    )
    def get(self, request: Request) -> Response:
        dummy_user = User(
            email="mock@example.com",
            nickname="mockuser",
            name="김철수",
            phone_number="01012345678",
            birthday="2000-01-01",
            profile_image_url="https://dummyimage.com/100x100",
            role=User.Role.STUDENT,
        )

        user_data = {
            "profile_image_url": dummy_user.profile_image_url,
            "email": dummy_user.email,
            "nickname": dummy_user.nickname,
            "name": dummy_user.name,
            "phone_number": dummy_user.phone_number,
            "birthday": dummy_user.birthday,
        }

        if dummy_user.role == User.Role.STUDENT:
            user_data.update(
                {
                    "course_name": "백앤드 개발",
                    "generation": "10기",
                }
            )

        return Response(user_data, status=status.HTTP_200_OK)


# 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=UserProfileUpdateSerializer,
        description="(Mock) 내 정보 수정 API",
        tags=["profile"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def put(self, request: Request) -> Response:

        serializer = UserProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        dummy_user = User(
            email="mock@example.com",
            nickname="mockuser",
            name="홍길동",
            phone_number="01012345678",
            birthday="1990-01-01",
            profile_image_url="https://dummyimage.com/100x100",
        )
        dummy_user.nickname = validated.get("nickname", dummy_user.nickname)
        dummy_user.phone_number = validated.get("phone_number", dummy_user.phone_number)

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
    permission_classes = [AllowAny]

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
