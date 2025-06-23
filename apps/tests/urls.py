# 예: tssts/urls.py
from django.urls import path
from .views.test_admin_view import test_validate_code_admin
from .views.test_user_view import test_validate_code_user

urlpatterns = [
    path("test-validate-code-admin/", test_validate_code_admin),
    path("test-validate-code-user/", test_validate_code_user),
]
