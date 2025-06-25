from django.urls import path

from apps.users.views.admin_user_views import (
    AdminUserDeleteView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserUpdateView,
)

urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<int:user_id>/update/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("users/<int:user_id>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),
    path("users/<int:user_id>/role/", AdminUserRoleUpdateView.as_view(), name="admin-user-role-update"),
]
