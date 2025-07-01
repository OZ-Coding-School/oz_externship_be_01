from django.urls import path

from apps.tests.views.admin_testquestion_views import (
    TestQuestionCreateView,
    TestQuestionListView,
    TestQuestionUpdateDeleteView,
)

from .views.admin_test_views import (
    AdminTestCreateAPIView,
    AdminTestDeleteAPIView,
    AdminTestDetailAPIView,
    AdminTestListView,
    AdminTestUpdateAPIView,
)
from .views.admin_testdeployments_views import TestValidateCodeAdminView, TestDeploymentCreateView, \
    TestDeploymentDeleteView, TestDeploymentStatusView, DeploymentListView, DeploymentDetailView
from .views.user_testdeployments_views import UserCodeValidationView

app_name = "tests"

urlpatterns = [
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", AdminTestCreateAPIView.as_view(), name="test-create"),
    path("test-questions/", TestQuestionCreateView.as_view(), name="test-question-create"),
    path("test-questions/<int:question_id>/", TestQuestionUpdateDeleteView.as_view(), name="test-question-detail"),
    path("tests/", TestQuestionListView.as_view(), name="test-question-list"),
    path("tests/validate-code/",TestValidateCodeAdminView.as_view(), name="admin-code-validate"),
    path("tests/validate-code/",UserCodeValidationView.as_view(), name="user-code-validate"),
    path("admin/test-deployments/(deployment_id}/", TestDeploymentDeleteView.as_view(), name="test-deployment-DeleteView"),
    path("admin/test-deployments/{deployment_id}/status/", TestDeploymentStatusView.as_view(), name="test-deployment-status"),
    path("admin/test-deployments/",DeploymentListView.as_view(), name="test-deployment-list"),
    path("admin/test-deployments/{deployment_id}/",DeploymentDetailView.as_view(), name="test-deployment-detail"),
    path("admin/test-deployments/", TestDeploymentCreateView.as_view(), name="test-deployment-create"),
    ]
