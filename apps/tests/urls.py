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
from .views.admin_testdeployments_views import (
    DeploymentDetailView,
    DeploymentListView,
    TestDeploymentCreateView,
    TestDeploymentDeleteView,
    TestDeploymentStatusView,
)
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
    # 참가 코드 검증 (Admin용)
    path("tests/validate-code/", UserCodeValidationView.as_view(), name="user-code-validate"),
    # 배포 상태 변경 (Activated ↔ Deactivated)
    path(
        "admin/test-deployments/<int:deployment_id>/status/",
        TestDeploymentStatusView.as_view(),
        name="test-deployment-status",
    ),
    # 배포 목록 조회
    path(
        "admin/test-deployments/",
        DeploymentListView.as_view(),
        name="test-deployment-list",
    ),
    # 배포 상세 조회
    path(
        "admin/test-deployments/<int:deployment_id>/",
        DeploymentDetailView.as_view(),
        name="test-deployment-detail",
    ),
    # 배포 생성
    path(
        "admin/test-deployments/create/",
        TestDeploymentCreateView.as_view(),
        name="test-deployment-create",
    ),
    # 배포 삭제
    path(
        "admin/test-deployments/<int:deployment_id>/delete/",
        TestDeploymentDeleteView.as_view(),
        name="test-deployment-delete",
    ),
]
