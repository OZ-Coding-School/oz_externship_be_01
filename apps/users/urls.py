from django.urls import path

from apps.users.views.auth.email_auth import SendEmailCodeView, VerifyEmailCodeView
from apps.users.views.auth.email_login import EmailLoginAPIView
from apps.users.views.auth.signup import SignUpAPIView
from apps.users.views.auth.social_login import KakaoLoginAPIView, NaverLoginAPIView


from django.urls import path

from apps.users.views.admin_enrollments_views import AdminApproveEnrollmentsView
from apps.users.views.admin_user_views import (
    AdminUserDeleteView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserUpdateView,
)
from apps.users.views.profile_views import (
    NicknameCheckView,
    UserProfileUpdateView,
    UserProfileView,
)
from apps.users.views.withdrawal_views import UserDeleteView, UserRestoreView

urlpatterns = [
    # auth 관련 url
    path("email/send-code", SendEmailCodeView.as_view(), name="send_email_code"),
    path("email/verify-code", VerifyEmailCodeView.as_view(), name="verify_email_code"),
    path("login/email", EmailLoginAPIView.as_view(), name="email_login"),
    path("signup", SignUpAPIView.as_view(), name="sign_up"),
    path("login/kakao", KakaoLoginAPIView.as_view(), name="kakao_login"),
    path("login/naver", NaverLoginAPIView.as_view(), name="naver_login"),


    path("users/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("users/restore/", UserRestoreView.as_view(), name="user-restore"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/update/", UserProfileUpdateView.as_view(), name="user-profile-update"),
    path("profile/nickname-check/", NicknameCheckView.as_view(), name="nickname-check"),
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
