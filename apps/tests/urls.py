from django.urls import path

from .views.admin_test_views import (
    AdminTestCreateAPIView,
    AdminTestDeleteAPIView,
    AdminTestDetailAPIView,
    AdminTestListView,
    AdminTestUpdateAPIView,
)

from .views.test_admin_view import (
    create_test_questions,
    delete_test_questions,
    list_test_questions,
    update_test_questions,
)

app_name = "tests"

urlpatterns = [
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", AdminTestCreateAPIView.as_view(), name="test-create"),
    path("test-questions/", create_test_questions, name="create-test-questions"),
    path("test-questions/<int:question_id>/", update_test_questions, name="update-test-questions"),
    path("test-questions/<int:question_id>/delete/", delete_test_questions, name="delete-test-questions"),
    path("test-questions/list/", list_test_questions, name="list-test-questions"),
]
