from unittest import mock

from django.urls import path

from apps.tests.views import test_admin_view
from apps.tests.views import test_user_view

urlpatterns = [
    path("test/submissions/start/", test_user_view.post_test_submission_start),
    path("test/submissions/<int:submission_id>/submit/", test_user_view.post_test_submission_submit),
    path("test/submissions/<int:submission_id>/result/", test_user_view.get_test_submission_result),

    # admin
    path("admin/test-submissions/", test_admin_view.admin_test_submissions),
    path("admin/test-submissions/{submission_id}/", test_admin_view.admin_test_submissions_detail),
    path("admin/test-submissions/{submissions_id}/", test_admin_view.admin_test_submissions_delete),

]