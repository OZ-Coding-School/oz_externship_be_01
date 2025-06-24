from unittest import mock

from django.urls import path

from apps.tests.views import test_admin_view, test_user_view

app_name = "tests"

urlpatterns = [
    path(
        "test/submissions/start/", test_user_view.TestSubmissionStartView.as_view(), name="submission_start"
    ),  # 쪽지 시험 응시
    path(
        "test/submissions/<int:submission_id>/submit/",
        test_user_view.TestSubmissionSubmitView.as_view(),
        name="submission_submit",
    ),  # 쪽지 시험 제출
    path(
        "test/submissions/<int:submission_id>/result/",
        test_user_view.TestSubmissionResultView.as_view(),
        name="submission_result",
    ),  # 쪽지 시험 결과 조회
    # admin
    path(
        "admin/test-submissions/",
        test_admin_view.AdminTestSubmissionsView.as_view(),
        name="admin_submission_detail_or_delete",
    ),  # 쪽지 시험 응시 내역 목록 조회
    path(
        "admin/test-submissions/<int:submission_id>/",
        test_admin_view.AdminTestSubmissionDetailDeleteView.as_view(),
        name="admin_submission_detail_or_delete",
    ),  # 쪽지 시험 응시 내역 상세 조회 및 삭제
]
