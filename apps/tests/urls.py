from django.urls import path

from .views.test_admin_view import (
    AdminTestDeleteAPIView,
    AdminTestListView,
    AdminTestUpdateAPIView,
    TestCreateAPIView,
    TestDetailAPIView,
)

app_name = "tests"

urlpatterns = [
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", TestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", TestCreateAPIView.as_view(), name="test-create"),
]
