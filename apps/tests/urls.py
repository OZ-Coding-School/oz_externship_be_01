# apps/tests/urls.py

from django.urls import path
from .views.test_user_view import mock_validate_code_user
from .views.test_admin_view import mock_validate_code_admin

urlpatterns = [
    path("mock/user/validate-code/", mock_validate_code_user, name="mock-user-code"),
    path("mock/admin/validate-code/", mock_validate_code_admin, name="mock-admin-code"),
]
