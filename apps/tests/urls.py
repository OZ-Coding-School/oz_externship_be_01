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
from .views.admin_testsubmission_views import (
    AdminTestSubmissionDeleteView,
    AdminTestSubmissionDetailView,
    AdminTestSubmissionsView,
)
from .views.user_testsubmission_views import (
    TestSubmissionResultView,
    TestSubmissionStartView,
    TestSubmissionSubmitView,
)

app_name = "tests"

urlpatterns = [
    # 쪽지 시험 응시
    path(
        "test/submissions/<int:test_id>/start/",
        TestSubmissionStartView.as_view(),
        name="submission_start",
    ),
    # 쪽지 시험 제출
    path(
        "test/submissions/<int:deployment_id>/submit/",
        TestSubmissionSubmitView.as_view(),
        name="submission_submit",
    ),
    # 쪽지 시험 결과 조회
    path(
        "test/submissions/<int:submission_id>/result/",
        TestSubmissionResultView.as_view(),
        name="submission_result",
    ),
    # admin
    # 쪽지 시험 응시 내역 전체 목록 조회
    path(
        "admin/test-submissions/",
        AdminTestSubmissionsView.as_view(),
        name="admin_submission_List",
    ),
    # 쪽지 시험 응시 내역 상세 조회
    path(
        "admin/test-submissions/<int:submission_id>",
        AdminTestSubmissionDetailView.as_view(),
        name="admin_submission_detail",
    ),
    # 쪽지 시험 응시 내역 삭제
    path(
        "admin/test-submissions/<int:submission_id>/delete",
        AdminTestSubmissionDeleteView.as_view(),
        name="admin_submission_delete",
    ),
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", AdminTestCreateAPIView.as_view(), name="test-create"),
    path("test-questions/", TestQuestionCreateView.as_view(), name="test-question-create"),
    path("test-questions/<int:question_id>/", TestQuestionUpdateDeleteView.as_view(), name="test-question-detail"),
    path("tests/", TestQuestionListView.as_view(), name="test-question-list"),
]
