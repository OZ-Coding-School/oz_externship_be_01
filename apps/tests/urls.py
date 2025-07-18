from django.urls import path

from apps.tests.views.admin_testquestion_views import (
    TestQuestionBulkUpdateAPIView,
    TestQuestionCreateView,
    TestQuestionUpdateDeleteView,
)

from .views.admin_dashboard_views import TestDashboardView
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
from .views.admin_testsubmission_views import (
    AdminTestSubmissionDeleteView,
    AdminTestSubmissionDetailView,
    AdminTestSubmissionsView,
)
from .views.user_deploymentstatus_views import UserTestDeploymentStatusView
from .views.user_testdeployments_views import (
    TestDeploymentListView,
    UserCodeValidationView,
)
from .views.user_testsubmission_views import (
    TestStartView,
    TestSubmissionResultView,
    TestSubmissionSubmitView,
)

app_name = "tests"

urlpatterns = [
    # USER
    path(
        "test/submissions/<int:test_deployment_id>/start/",
        TestStartView.as_view(),
        name="submission_start",
    ),
    path(
        "test/submissions/<int:deployment_id>/submit/",
        TestSubmissionSubmitView.as_view(),
        name="submission_submit",
    ),
    path(
        "test/submissions/<int:submission_id>/result/",
        TestSubmissionResultView.as_view(),
        name="submission_result",
    ),
    path(
        "test/deployments",
        TestDeploymentListView.as_view(),
        name="deployment_list",
    ),
    # 참가 코드 검증
    path("tests/<int:test_deployment_id>/validate/", UserCodeValidationView.as_view(), name="user-code-validate"),
    path(
        "tests/<int:test_deployment_id>/validate-status/",
        UserTestDeploymentStatusView.as_view(),
        name="user-test-deployment-status",
    ),
    # ADMIN
    path("admin/tests/dashboard/", TestDashboardView.as_view(), name="admin-test-dashboard"),
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create/", AdminTestCreateAPIView.as_view(), name="test-create"),
    path("admin/test-questions/", TestQuestionCreateView.as_view(), name="test-question-create"),
    path(
        "admin/test-questions/<int:question_id>/", TestQuestionUpdateDeleteView.as_view(), name="test-question-detail"
    ),
    path(
        "admin/tests-questions/bulk-update/", TestQuestionBulkUpdateAPIView.as_view(), name="test-question-bulk-update"
    ),
    path(
        "admin/test-submissions/",
        AdminTestSubmissionsView.as_view(),
        name="admin_submission_List",
    ),
    path(
        "admin/test-submissions/<int:submission_id>",
        AdminTestSubmissionDetailView.as_view(),
        name="admin_submission_detail",
    ),
    path(
        "admin/test-submissions/<int:submission_id>/delete",
        AdminTestSubmissionDeleteView.as_view(),
        name="admin_submission_delete",
    ),
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
