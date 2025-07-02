from rest_framework.permissions import BasePermission


class IsAdminOrStaffByGroup(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.groups.filter(name_in=["관리자", "조교", "러닝코치", "운영매니저"]).exists()
        )
