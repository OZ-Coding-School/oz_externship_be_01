from django.conf import settings
from rest_framework.permissions import BasePermission

from apps.users.models import User


# 관리자(ADMIN) 또는 스태프(OM: 운영매니저, LC: 러닝코치, TA: 조교) 역할을 가진 사용자만 허용
class IsAdminOrStaff(BasePermission):

    message = "관리자 또는 스태프 권한이 필요합니다."

    def has_permission(self, request, view):

        # 개발환경(DEBUG=True)에서는 무조건 허용

        if settings.DEBUG:
            # print("[INFO] DEBUG 모드: permission 우회 허용")
            return True

        user = request.user

        # 인증되지 않은 사용자면 거부
        if not user or not user.is_authenticated:
            return False

        # User.Role.choices 기반으로 GENERAL, STUDENT만 제외하고 나머지 역할을 허용
        excluded_roles = {User.Role.GENERAL, User.Role.STUDENT}
        allowed_roles = [role for role, _ in User.Role.choices if role not in excluded_roles]

        if user.role in allowed_roles:
            return True

        # 위 조건을 모두 통과하지 못하면 접근 거부
        return False
