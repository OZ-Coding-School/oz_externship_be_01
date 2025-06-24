from unittest import mock

from django.urls import path

from apps.tests.views import test_admin_view, test_user_view

app_name = "tests"

urlpatterns = [
    path("test/submissions/start/", test_user_view.post_test_submission_start, name="submission_start"),
    path(
        "test/submissions/<int:submission_id>/submit/",
        test_user_view.post_test_submission_submit,
        name="submission_submit",
    ),
    path(
        "test/submissions/<int:submission_id>/result/",
        test_user_view.get_test_submission_result,
        name="submission_result",
    ),
    # admin
    path("admin/test-submissions/", test_admin_view.admin_test_submissions, name="admin_submission_detail_or_delete"),
    path(
        "admin/test-submissions/<int:submission_id>/",
        test_admin_view.admin_test_submissions_detail,
        name="admin_submission_detail_or_delete",
    ),
    # path(
    #     "admin/test-submissions/<int:submission_id>/",
    #     test_admin_view.admin_test_submissions_delete,
    #     name="admin_submission_delete",
    # ),
]
