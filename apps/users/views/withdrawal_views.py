from typing import Any, cast

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.withdrawal_serializers import (
    UserDeleteSerializer,
    UserRestoreSerializer,
)

# 회원탈퇴 및 회원 복구 API
# Soft Delete를 적용하며 회원탈퇴 후 2주 후에 Batch 작업으로 회원과 관련된 모든 데이터를 삭제
# User 모델 수정전 Withdrawal 모델 없음, 모델 메서드 없이 처리(mockapi만)

User = get_user_model()


# 회원 탈퇴 Mock API
class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = UserDeleteSerializer(data=request.data)

        if serializer.is_valid():
            user = cast(Any, request.user)

            # soft delete view 에서 바로 처리
            user.is_deleted = True
            user.is_active = False
            user.deleted_reason = serializer.validated_data.get("reason")
            user.deleted_detail = serializer.validated_data.get("detail")
            user.deleted_at = timezone.now()
            user.save()

            return Response({"message": "탈퇴 완료되었습니다."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 회원 복구 Mock API
class UserRestoreView(APIView):
    def post(self, request: Request) -> Response:
        serializer = UserRestoreSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            verification_code = serializer.validated_data["verification_code"]

            try:
                user = cast(Any, User.objects.get(email=email, is_deleted=True))
            except User.DoesNotExist:
                return Response({"error": "탈퇴된 계정을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            if verification_code == "123456":  # 임의 코드
                user.is_deleted = False
                user.is_active = True
                user.deleted_reason = ""
                user.deleted_detail = ""
                user.deleted_at = None
                user.save()

                return Response({"message": "계정 복구 완료"}, status=status.HTTP_200_OK)

            return Response({"error": "인증 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
