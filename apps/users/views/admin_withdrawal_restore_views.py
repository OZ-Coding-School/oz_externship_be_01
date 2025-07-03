from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.permissions import PermissionsStaff, PermissionsTrainingAssistant
from apps.users.serializers.admin_withdrawal_restore_serializers import (
    AdminWithdrawalRestoreSerializer,
)


# 권환 확인
class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and (
            user.is_role
            or PermissionsStaff.objects.filter(user=user).exists()
            or PermissionsTrainingAssistant.objects.filter(user=user).exists()
        ):
            return True
        raise PermissionDenied(detail="해당 작업을 수행할 권한이 없습니다.")


class AdminWithdrawalRestoreAPIView(APIView):
    permission_classes = [AllowAny]  # JWT > IsAdminOrStaff 로 수정

    @extend_schema(tags=["withdrawal"], summary="어드민 회원탈퇴 복구")
    def post(self, request, user_id):
        data = request.data
        data["user_id"] = user_id
        serializer = AdminWithdrawalRestoreSerializer(data=data)
        if serializer.is_valid():
            result = serializer.restore_user()
            return Response(result, status=status.HTTP_200_OK)
        error_list = serializer.errors.get("non_field_errors", ["해당 탈퇴 사용자를 찾을 수 없습니다."])
        return Response({"message": error_list[0]}, status=status.HTTP_400_BAD_REQUEST)
