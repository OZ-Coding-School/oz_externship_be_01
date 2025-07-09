import uuid

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
    UserProfileUpdateResponseSerializer,
    UserProfileUpdateSerializer,
)
from apps.users.utils.nickname_validators import is_nickname_duplicated
from core.utils.s3_file_upload import S3Uploader


# 프로필 확인
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="내 정보 조회 API",
        tags=["user-profile"],
        responses={200: UserProfileSerializer},
    )
    def get(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=UserProfileUpdateSerializer,
        description="내 정보 수정 API",
        tags=["user-profile"],
        responses={200: UserProfileUpdateResponseSerializer},
    )
    def patch(self, request: Request) -> Response:
        user = request.user
        assert isinstance(user, User)

        serializer = UserProfileUpdateSerializer(
            instance=user,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        # 기본 이미지 삭제->프로필 업로드
        if "profile_image_file" in request.FILES:
            file_obj = request.FILES["profile_image_file"]
            uploader = S3Uploader()

            # 기존 이미지가 있는 경우 → 삭제 시도
            if user.profile_image_url:
                delete_success = uploader.delete_file(user.profile_image_url)

                if not delete_success:
                    return Response(
                        {"message": "기존 프로필 이미지 삭제에 실패했습니다."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            # 새 프로필 이미지 업로드
            filename = f"{user.id}_{uuid.uuid4().hex}_{file_obj.name}"
            s3_key = f"users/profile/{filename}"
            uploaded_url = uploader.upload_file(file_obj, s3_key)

            if not uploaded_url:
                return Response(
                    {"message": "프로필 이미지 업로드에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            serializer.validated_data["profile_image_url"] = uploaded_url

        serializer.save(instance=user)

        response_data = {
            "message": "내 정보 수정 완료",
            "updated_fields": {
                "nickname": serializer.validated_data.get("nickname", user.nickname),
                "phone_number": serializer.validated_data.get("phone_number", user.phone_number),
                "profile_image_url": serializer.validated_data.get("profile_image_url", user.profile_image_url),
            },
        }
        response_serializer = UserProfileUpdateResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# 닉네임 중복 확인
class NicknameCheckView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=NicknameCheckSerializer,
        description="닉네임 중복 확인 API",
        tags=["user-profile"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nickname = serializer.validated_data["nickname"]

        if is_nickname_duplicated(nickname):
            return Response({"message": "이미 사용 중인 닉네임입니다."}, status=400)

        return Response({"message": "사용 가능한 닉네임입니다."})
