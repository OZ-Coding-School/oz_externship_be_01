from typing import Any, Dict

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin_user_serializers import (
    AdminUserRoleUpdateSerializer,
    AdminUserSerializer,
    PaginatedAdminUserListSerializer,
)

User = get_user_model()


# 어드민 유저 목록 조회
class AdminUserListView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminUserSerializer

    @extend_schema(
        summary="어드민 회원 목록 조회",
        description="""
        어드민이 전체 유저 목록을 조회합니다.

        - `joined_at`: 회원가입일 (`users.created_at`)
        - `withdrawal_requested_at`: 탈퇴 요청일 (`withdrawals.created_at`, 탈퇴 요청이 없으면 None)
        """,
        responses={
            200: PaginatedAdminUserListSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
        },
    )
    def get(self, request: Request) -> Response:
        mock_response: Dict[str, Any] = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "email": "admin@example.com",
                    "name": "홍길동",
                    "nickname": "hongkildong",
                    "birthday": "1998-08-16",
                    "role": "ADMIN",
                    "is_active": True,
                    "joined_at": "2024-01-01T10:00:00Z",
                    "withdrawal_requested_at": None,
                },
                {
                    "id": 2,
                    "email": "student@example.com",
                    "name": "김수강",
                    "nickname": "learner_kim",
                    "birthday": "2000-01-05",
                    "role": "STUDENT",
                    "is_active": True,
                    "joined_at": "2024-02-10T15:30:00Z",
                    "withdrawal_requested_at": None,
                },
            ],
        }

        serializer = PaginatedAdminUserListSerializer(instance=mock_response)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 어드민 회원 상세 조회
class AdminUserDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminUserSerializer

    @extend_schema(
        summary="어드민 회원 상세 조회",
        description="어드민이 전체 유저 상세 정보를 조회합니다.",
        responses={200: AdminUserSerializer, 400: OpenApiResponse(description="존재하지 않는 유저입니다.")},
    )
    def get(self, request: Request, user_id: int) -> Response:
        data = {"id": user_id}
        serializer = AdminUserSerializer(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 어드민 회원 정보 수정
class AdminUserUpdateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminUserSerializer

    @extend_schema(
        summary="어드민 회원 정보 수정",
        description="어드민이 특정 회원 정보를 수정합니다.",
        request=AdminUserSerializer,
        responses={
            200: OpenApiResponse(description="수정된 유저의 상세 정보를 반환합니다.", response=AdminUserSerializer),
            400: OpenApiResponse(description="잘못된 요청입니다."),
        },
    )
    def patch(self, request: Request, user_id: int) -> Response:
        modifiable_fields = ["name", "nickname", "phone_number", "self_introduction", "profile_image_url", "is_active"]

        serializer = self.serializer_class(
            data=request.data, partial=True, fields=modifiable_fields, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        updated_user_data = {"id": user_id, **serializer.validated_data}
        response_serializer = self.serializer_class(instance=updated_user_data)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


# 어드민 회원 삭제
class AdminUserDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="어드민 회원 삭제",
        description="어드민이 특정 회원을 삭제합니다.",
        responses={
            204: OpenApiResponse(description=""),
            404: OpenApiResponse(description="해당 사용자를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, user_id: int) -> Response:
        if not isinstance(user_id, int) or user_id <= 0:
            return Response({"detail": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 삭제 동작 없이 삭제 성공 응답만 반환
        return Response(status=status.HTTP_204_NO_CONTENT)


# 어드민 회원 권한 변경
class AdminUserRoleUpdateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminUserRoleUpdateSerializer

    @extend_schema(
        summary="어드민 회원 권한 변경",
        description="어드민 전용 회원의 권한을 변경합니다.",
        request=AdminUserRoleUpdateSerializer,
        responses={
            200: OpenApiResponse(description="유저의 상세 정보를 반환합니다.", response=AdminUserSerializer),
            400: OpenApiResponse(description="유효하지 않은 권한입니다."),
        },
    )
    def patch(self, request: Request, user_id: int) -> Response:
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated_role = serializer.validated_data["role"]

        user = User(id=user_id, role=validated_role)

        # 응답 직렬화 (전체 유저 정보)
        response_serializer = AdminUserSerializer(instance=user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
