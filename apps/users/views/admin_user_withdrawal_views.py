from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tests.permissions import IsAdminOrStaff
from apps.users.models.withdrawals import Withdrawal
from apps.users.serializers.admin_user_withdrawal_serializers import (
    AdminListWithdrawalSerializer,
    WithdrawalResponseSerializer,
)
from apps.users.views.admin_user_views import AdminUserListPaginator


# 어드민 회원 탈퇴 상세조회
class AdminDetailWithdrawalView(APIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = WithdrawalResponseSerializer

    @extend_schema(tags=["Admin - 유저 회원탈퇴"], summary="어드민 회원 탈퇴 상세 조회(기능구현완료)")
    def get(self, request: Request, withdrawal_id: int) -> Response:
        try:
            withdrawal = Withdrawal.objects.select_related("user").get(id=withdrawal_id)
        except Withdrawal.DoesNotExist:
            return Response({"detail": "탈퇴 내역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WithdrawalResponseSerializer(withdrawal)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminListWithdrawalView(APIView):
    permission_classes = [IsAdminOrStaff]

    @extend_schema(tags=["Admin - 유저 회원탈퇴"], summary="어드민 회원 탈퇴 목록 조회(기능구현완료)")
    def get(self, request):
        # /?search={jee}
        search = request.query_params.get("search")
        # /?ordering={latest or oldest}
        ordering = request.query_params.get("ordering", "id")
        # /?role={STUDENT}
        role = request.query_params.get("role")

        withdrawals = Withdrawal.objects.select_related("user").all()

        if search:
            withdrawals = withdrawals.filter(Q(user__email__icontains=search) | Q(user__name__icontains=search))

        if role:
            withdrawals = withdrawals.filter(user__role=role.upper())

        if ordering == "latest":
            withdrawals = withdrawals.order_by("-created_at")
        elif ordering == "oldest":
            withdrawals = withdrawals.order_by("created_at")
        else:
            withdrawals = withdrawals.order_by("id")

        paginator = AdminUserListPaginator()
        paginated_qs = paginator.paginate_queryset(withdrawals, request)
        serializer = AdminListWithdrawalSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)
