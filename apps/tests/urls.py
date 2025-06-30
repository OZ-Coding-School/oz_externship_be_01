from unittest import mock

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

app_name = "tests"

from apps.tests.views import test_admin_view
from apps.tests.views import test_user_view

urlpatterns = [
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", AdminTestCreateAPIView.as_view(), name="test-create"),
    path("test-questions/", TestQuestionCreateView.as_view(), name="test-question-create"),
    path("test-questions/<int:question_id>/", TestQuestionUpdateDeleteView.as_view(), name="test-question-detail"),
    path("tests/", TestQuestionListView.as_view(), name="test-question-list"),
    path("test/submissions/start/", test_user_view.post_test_submission_start),
    path("test/submissions/<int:submission_id>/submit/", test_user_view.post_test_submission_submit),
    path("test/submissions/<int:submission_id>/result/", test_user_view.get_test_submission_result),

    # admin
    path("admin/test-submissions/", test_admin_view.admin_test_submissions),
    path("admin/test-submissions/{submission_id}/", test_admin_view.admin_test_submissions_detail),
    path("admin/test-submissions/{submissions_id}/", test_admin_view.admin_test_submissions_delete),
]
