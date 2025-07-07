import uuid

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import EnrollmentRequest
from apps.users.models import User
from apps.users.serializers.profile_serializers import (
    NicknameCheckSerializer,
    UserProfileSerializer,
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

        user_data = {
            "profile_image_url": user.profile_image_url,
            "email": user.email,
            "name": user.name,
            "nickname": user.nickname,
            "phone_number": user.phone_number,
            "birthday": user.birthday,
        }

        if user.role == user.Role.STUDENT:
            enrollment = (
                EnrollmentRequest.objects.filter(user=user)
                .select_related("generation__course")
                .order_by("-created_at")
                .first()
            )
            if enrollment:
                course_name = enrollment.generation.course.name
                generation_number = f"{enrollment.generation.number}기"
            else:
                course_name = None
                generation_number = None

            user_data.update(
                {
                    "course_name": course_name,
                    "generation": generation_number,
                }
            )

        return Response(user_data, status=status.HTTP_200_OK)


# 프로필 수정
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        request=UserProfileUpdateSerializer,
        description="내 정보 수정 API",
        tags=["user-profile"],
        responses={200: OpenApiTypes.OBJECT},
    )
    def put(self, request: Request) -> Response:

        serializer = UserProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        user = request.user
        assert isinstance(user, User)

        # 기본 이미지 삭제->프로필 업로드
        if "profile_image_file" in request.FILES:
            file_obj = request.FILES["profile_image_file"]
            uploader = S3Uploader()

            # 기본이미지 삭제
            if user.profile_image_url:
                uploader.delete_file(user.profile_image_url)

            # 새 프로필 이미지 업로드
            filename = f"{user.id}_{uuid.uuid4().hex}_{file_obj.name}"
            s3_key = f"users/profile/{filename}"
            uploaded_url = uploader.upload_file(file_obj, s3_key)

            if not uploaded_url:
                return Response(
                    {"message": "프로필 이미지 업로드에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            user.profile_image_url = uploaded_url

        user.save()

        if "nickname" in validated:
            new_nickname = validated["nickname"]
            if is_nickname_duplicated(new_nickname, user_id=user.id):
                return Response({"message": "이미 사용 중인 닉네임입니다."}, status=400)
            user.nickname = new_nickname

        # 휴대폰번호 인증 구현 되면 수정 예정
        if "phone_number" in validated:
            user.phone_number = validated["phone_number"]

        if "password" in validated:
            user.set_password(validated["password"])

        return Response(
            {
                "message": "내 정보 수정 완료",
                "updated_fields": {
                    "nickname": user.nickname,
                    "phone_number": user.phone_number,
                    "profile_image_url": user.profile_image_url,
                },
            },
            status=status.HTTP_200_OK,
        )


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
