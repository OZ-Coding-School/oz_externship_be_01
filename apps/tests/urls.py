from django.urls import path

from .views.test_admin_view import (
    DeleteMiniTestDeploymentView,
    DeploymentDetailView,
    DeploymentListView,
    TestDeploymentCreateView,
    TestDeploymentStatusView,
    TestValidateCodeAdminView,
)
from .views.test_user_view import TestValidateCodeUserView

urlpatterns = [
    path("api/v1/tests/validate-code-admin/", TestValidateCodeAdminView.as_view(), name="test-validate-code-admin"),
    path(
        "api/v1/tests/validate-code-user/", TestValidateCodeUserView.as_view(), name="test-validate-code-user"
    ),  # 배포 내역 조회 (GET)
    path(
        "api/v1/admin/test-deployments/<int:deployment_id>/",
        DeploymentDetailView.as_view(),
        name="test-deployment-detail",
    ),
    # 배포 생성 (create)
    path("api/v1/admin/test-deployments/", TestDeploymentCreateView.as_view(), name="test-deployment-create"),
    # 배포 삭제 (DELETE)
    path(
        "api/v1/admin/test-deployments/<int:deployment_id>/delete/",
        DeleteMiniTestDeploymentView.as_view(),
        name="delete-mini-test-deployment",
    ),
    # 배포 목록 조회
    path("api/v1/admin/test-deployments/", DeploymentListView.as_view(), name="test-deployment-list"),
    # 배포 내역 조회
    path(
        "api/v1/admin/test-deployments/<int:deployment_id>/",
        DeploymentDetailView.as_view(),
        name="test-deployment-detail",
    ),
]
