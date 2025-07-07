from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff, IsAdminRole
from apps.users.models import User
from apps.users.serializers.admin_user_serializers import (
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserRoleUpdateSerializer,
    AdminUserSerializer,
    PaginatedAdminUserListSerializer,
)


class AdminUserListPaginator(PageNumberPagination):
    page_size = 5
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100


# 어드민 유저 목록 조회
class AdminUserListView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = AdminUserListSerializer
    pagination_class = AdminUserListPaginator

    @extend_schema(
        summary="어드민 회원 목록 조회",
        description="""
            어드민, 조교, 운영매니저, 러닝코치 권한을 가진 사용자가 회원 목록을 조회합니다.

            - `joined_at`: 회원가입일 (`user.created_at`)
            - `withdrawal_requested_at`: 탈퇴 요청일 (`withdrawal.created_at`, 없으면 null)
            """,
        responses={
            200: PaginatedAdminUserListSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
        tags=["Admin - 회원 관리"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            queryset: QuerySet[User] = User.objects.select_related("withdrawal")

            # 검색
            search = request.query_params.get("search", "").strip()
            if search:
                queryset = queryset.filter(
                    Q(email__icontains=search) | Q(nickname__icontains=search) | Q(name__icontains=search)
                )

            # 권한 필터
            role = request.query_params.get("role", "").upper()
            if role:
                valid_roles = [choice[0] for choice in User.Role.choices]
                if role not in valid_roles:
                    return Response(
                        {"detail": f"유효하지 않은 권한입니다. 사용 가능한 값: {', '.join(valid_roles)}"}, status=400
                    )
                queryset = queryset.filter(role=role)

            # 활성/비활성 필터
            is_active = request.query_params.get("is_active", "").lower()
            if is_active == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active == "false":
                queryset = queryset.filter(is_active=False)

            # 정렬
            ordering = request.query_params.get("ordering", "-created_at")
            queryset = queryset.order_by(ordering)

            # 페이지네이션
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)

            if page is None:
                raise NotFound("페이지 범위를 벗어났습니다.")

            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except ValidationError:
            return Response({"detail": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as nf:
            return Response({"detail": str(nf)}, status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response({"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, status=500)


# 어드민 회원 상세 조회
class AdminUserDetailView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = AdminUserDetailSerializer

    @extend_schema(
        summary="어드민 회원 상세 조회",
        description="""
            스태프 및 어드민은 회원 목록에서 특정 회원의 상세 정보를 조회할 수 있습니다.
            반환 항목은 해당 회원의 역할에 따라 달라집니다.
            """,
        responses={
            200: AdminUserDetailSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
            404: OpenApiResponse(description="존재하지 않는 유저입니다."),
        },
        tags=["Admin - 회원 관리"],
    )
    def get(self, request: Request, user_id: int) -> Response:
        try:
            user = (
                User.objects.prefetch_related(
                    "ta_permissions__generation__course",
                    "staff_permissions__course",
                    "student_permissions__generation__course",
                )
                .get(id=user_id)
            )

        except User.DoesNotExist:
            return Response({"detail": "존재하지 않는 유저입니다."}, status=404)

        serializer = self.serializer_class(user)
        return Response(serializer.data, status=200)


# 어드민 회원 정보 수정
class AdminUserUpdateView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminUserSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary="어드민 회원 정보 수정",
        description="어드민이 특정 회원 정보를 수정합니다.",
        request=AdminUserSerializer,
        responses={
            200: OpenApiResponse(description="수정된 유저의 상세 정보를 반환합니다.", response=AdminUserSerializer),
            400: OpenApiResponse(description="잘못된 요청입니다."),
            404: OpenApiResponse(description="존재하지 않는 유저입니다."),
        },
        tags=["Admin - 회원 관리"],
    )
    def patch(self, request: Request, user_id: int) -> Response:
        mock_user = User(
            id=user_id,
            email="admin@example.com",
            name="홍길동",
            nickname="hongkildong",
            birthday=date(1998, 8, 16),
            gender="MALE",
            phone_number="010-0000-0000",
            self_introduction="안녕하세요",
            profile_image_url="media/users/profile_images/example.png",
            role="ADMIN",
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        serializer = self.serializer_class(
            instance=mock_user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        mock_user.name = serializer.validated_data.get("name")
        mock_user.gender = serializer.validated_data.get("gender")
        mock_user.phone_number = serializer.validated_data.get("phone_number")
        profile_img_file = serializer.validated_data.get("profile_image_file")
        mock_user.profile_image_url = (
            f"media/users/profile_images/{profile_img_file}"
            if profile_img_file is not None
            else mock_user.profile_image_url
        )
        mock_user.self_introduction = serializer.validated_data.get("self_introduction")

        response_serializer = self.serializer_class(instance=mock_user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# 어드민 회원 삭제
class AdminUserDeleteView(APIView):
    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="어드민 회원 삭제",
        description="어드민이 특정 회원을 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="존재하지 않는 유저입니다."),
        },
        tags=["Admin - 회원 관리"],
    )
    def delete(self, request: Request, user_id: int) -> Response:
        user = get_object_or_404(User, id=user_id)

        # 자기 자신은 삭제하지 못하도록 방지
        if request.user.id == user.id:
            return Response({"detail": "자기 자신은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
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
            404: OpenApiResponse(description="존재하지 않는 유저입니다."),
        },
        tags=["Admin - 회원 관리"],
    )
    def patch(self, request: Request, user_id: int) -> Response:
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_role = serializer.validated_data.get("role")

        mock_user = User(
            id=user_id,
            email="admin@example.com",
            name="홍길동",
            nickname="hongkildong",
            birthday=date(1998, 8, 16),
            gender="MALE",
            phone_number="010-0000-0000",
            self_introduction="안녕하세요",
            profile_image_url="",
            role=validated_role,
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        response_serializer = AdminUserSerializer(instance=mock_user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
