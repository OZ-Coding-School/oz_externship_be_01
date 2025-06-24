from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views.test_admin_view import (
    create_test_questions,
    delete_test_questions,
    list_test_questions,
    update_test_questions,
)

app_name = "tests"

urlpatterns = [
    path("test-questions/", create_test_questions, name="create-test-questions"),
    path("test-questions/<int:question_id>/", update_test_questions, name="update-test-questions"),
    path("test-questions/<int:question_id>/delete/", delete_test_questions, name="delete-test-questions"),
    path("test-questions/list/", list_test_questions, name="list-test-questions"),
]
