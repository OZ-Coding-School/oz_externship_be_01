from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin_withdrawal_restore_serializers import (
    AdminWithdrawalRestoreSerializer,
)


# 권환 확인
class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.role in ["ADMIN", "TA", "OM", "LC"]:
            raise PermissionDenied(detail="해당 작업을 수행할 권한이 없습니다.")
        return True


class AdminWithdrawalRestoreAPIView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(
        tags=["Admin - 유저 회원탈퇴"],
        summary="어드민 회원탈퇴 복구(기능구현완료)",
        description="관리자 권한으로 탈퇴한 회원의 계정을 복구합니다(기능구현 완료).",
    )
    def post(self, request, user_id):
        data = request.data
        data["user_id"] = user_id
        serializer = AdminWithdrawalRestoreSerializer(data=data)
        if serializer.is_valid():
            serializer.restore_user()
            return Response({"message": "사용자 계정이 성공적으로 복구되었습니다."}, status=status.HTTP_200_OK)
        error_list = serializer.errors.get("non_field_errors", ["해당 탈퇴 사용자를 찾을 수 없습니다."])
        return Response({"message": error_list[0]}, status=status.HTTP_400_BAD_REQUEST)
