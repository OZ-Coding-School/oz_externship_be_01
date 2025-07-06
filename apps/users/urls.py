from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views.admin_dashboard_views import (
    AdminEnrollmentTrendView,
    AdminJoinTrendView,
    AdminWithdrawalReasonPieView,
    AdminWithdrawalReasonTrendView,
    AdminWithdrawTrendView,
)
from apps.users.views.admin_enrollments_approve_views import AdminApproveEnrollmentsView
from apps.users.views.admin_enrollments_list_views import (
    AdminEnrollmentListView,
)
from apps.users.views.admin_enrollments_rejection_views import (
    RejectEnrollmentRequestView,
)
from apps.users.views.admin_user_views import (
    AdminUserDeleteView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserUpdateView,
)
from apps.users.views.admin_user_withdrawal_views import AdminDetailWithdrawalView
from apps.users.views.admin_withdrawal_restore_views import (
    AdminWithdrawalRestoreAPIView,
)
from apps.users.views.auth.email_auth import SendEmailCodeView, VerifyEmailCodeView
from apps.users.views.auth.email_login import EmailLoginAPIView
from apps.users.views.auth.signup import SignUpAPIView
from apps.users.views.auth.social_login import (
    KakaoLoginAPIView,
    NaverLoginAPIView,
)
from apps.users.views.find_account_views import (
    EmailFindView,
    PasswordChangeView,
    PasswordResetEmailSendView,
    PasswordResetVerifyCodeView,
)
from apps.users.views.profile_views import (
    NicknameCheckView,
    UserProfileUpdateView,
    UserProfileView,
)
from apps.users.views.student_enrollments_views import EnrollmentRequestView
from apps.users.views.withdrawal_views import UserDeleteView, UserRestoreView

urlpatterns = [
    # auth 관련 url
    path("email/send-code", SendEmailCodeView.as_view(), name="send_email_code"),
    path("email/verify-code", VerifyEmailCodeView.as_view(), name="verify_email_code"),
    path("login/email", EmailLoginAPIView.as_view(), name="email_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("signup", SignUpAPIView.as_view(), name="sign_up"),
    path("login/kakao", KakaoLoginAPIView.as_view(), name="kakao_login"),
    path("login/naver", NaverLoginAPIView.as_view(), name="naver_login"),
    path("users/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("users/restore/", UserRestoreView.as_view(), name="user-restore"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/update/", UserProfileUpdateView.as_view(), name="user-profile-update"),
    path("profile/nickname-check/", NicknameCheckView.as_view(), name="nickname-check"),
    # admin 유저 관리
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:user_id>/update/", AdminUserUpdateView.as_view(), name="admin-user-update"),
    path("admin/users/<int:user_id>/delete/", AdminUserDeleteView.as_view(), name="admin-user-delete"),
    path("admin/users/<int:user_id>/role/", AdminUserRoleUpdateView.as_view(), name="admin-user-role-update"),
    path("admin/users/student-enrollments/", AdminEnrollmentListView.as_view(), name="admin-student-enrollments-list"),
    # 수강생 전환 추세
    path("admin/users/dashboard/enrollment/", AdminEnrollmentTrendView.as_view(), name="admin-enrollment-trend"),
    # 회원가입 추세
    path("admin/users/dashboard/join/", AdminJoinTrendView.as_view(), name="admin-join-trend"),
    # 회원 탈퇴 추세
    path("admin/users/dashboard/withdraw/", AdminWithdrawTrendView.as_view(), name="admin-withdraw-trend"),
    # 탈퇴 사유 통계 (원형)
    path(
        "admin/users/dashboard/withdrawal-reasons/pie/",
        AdminWithdrawalReasonPieView.as_view(),
        name="admin-withdrawal-reason-pie",
    ),
    # 탈퇴 사유 추이 (막대/꺾은선)
    path(
        "admin/users/dashboard/withdrawal-reasons/trend/",
        AdminWithdrawalReasonTrendView.as_view(),
        name="admin-withdrawal-reason-trend",
    ),
    path("account/find-email/", EmailFindView.as_view(), name="find-email"),
    path("account/send-reset-code/", PasswordResetEmailSendView.as_view(), name="send-reset-code"),
    path("account/verify-code/", PasswordResetVerifyCodeView.as_view(), name="verify-code"),
    path("account/change-password/", PasswordChangeView.as_view(), name="change-password"),
    path(
        "admin/users/student-enrollments/approve/",
        AdminApproveEnrollmentsView.as_view(),
        name="admin-student-enrollments-approve",
    ),
    path("admin/withdrawal/<int:withdrawal_id>", AdminDetailWithdrawalView.as_view(), name="admin-withdrawal-detail"),
    path(
        "admin/users/student-enrollments/reject/",
        RejectEnrollmentRequestView.as_view(),
        name="admin-student-enrollments-reject",
    ),
    path("users/student/enrollments/", EnrollmentRequestView.as_view(), name="enrollment-requests"),
    path(
        "admin/withdrawal/<int:user_id>/restore/",
        AdminWithdrawalRestoreAPIView.as_view(),
        name="admin-withdraw-restore",
    ),
]
