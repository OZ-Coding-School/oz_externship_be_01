from rest_framework.views import APIView
from apps.users.serializers.admin_user_withdrawal_serializers import AdminUserWithdrawalSerializer

class AdminDetailWithdrawalView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminDetailWithdrawalSerializer

    def get(self, request, withdrawal_id):
        pass