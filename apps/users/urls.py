from django.urls import path
from apps.users.views.withdrawal_views import UserDeleteView, UserRestoreView

from apps.users.views.admin_enrollments_views import AdminApproveEnrollmentsView
from apps.users.views.admin_user_views import (
    AdminUserDeleteView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("api/users/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("api/users/restore/", UserRestoreView.as_view(), name="user-restore"),

    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:user_id>/update/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("admin/users/<int:user_id>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),
    path("admin/users/<int:user_id>/role/", AdminUserRoleUpdateView.as_view(), name="admin-user-role-update"),
    path(
        "admin/users/student-enrollments/approve/",
        AdminApproveEnrollmentsView.as_view(),
        name="admin-student-enrollments-approve",
    ),
]
