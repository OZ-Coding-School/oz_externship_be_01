from django.urls import path

from apps.users.views.admin_user_views import (
    AdminUserDeleteView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:user_id>/update/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("admin/users/<int:user_id>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),
    path("admin/users/<int:user_id>/role/", AdminUserRoleUpdateView.as_view(), name="admin-user-role-update"),
]
