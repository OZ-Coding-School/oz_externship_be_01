from django.urls import path
from .views.test_admin_view import (
    TestValidateCodeAdminView,
    TestDeploymentStatusView,
    DeleteMiniTestDeploymentView,
)
from .views.test_user_view import TestValidateCodeUserView

urlpatterns = [
    path("/api/v1/tests/validate-code-user/", TestValidateCodeAdminView.as_view(), name="test-validate-code-admin"),
    path("/api/v1/tests/validate-code-admin/", TestValidateCodeUserView.as_view(), name="test-validate-code-user"),
    path("/api/v1/admin/test-deployments/{deployment_id}/status/<int:deployment_id>/change-status/", TestDeploymentStatusView.as_view(), name="toggle-test-deployment-status"),
    path("/api/v1/admin/test-deployments/{deployment_id}/", DeleteMiniTestDeploymentView.as_view(), name="delete-mini-test-deployment"),
]
