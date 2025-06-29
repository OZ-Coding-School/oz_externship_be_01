from unittest import mock

from django.urls import path

from apps.tests.views import test_admin_view, test_user_view

from .views.admin_test_views import (
    AdminTestCreateAPIView,
    AdminTestDeleteAPIView,
    AdminTestDetailAPIView,
    AdminTestListView,
    AdminTestUpdateAPIView,
)

app_name = "tests"

urlpatterns = [
    # 쪽지 시험 응시
    path(
        "test/submissions/<int:test_id>/start/",
        test_user_view.TestSubmissionStartView.as_view(),
        name="submission_start",
    ),  
    # 쪽지 시험 제출
    path(
        "test/submissions/<int:deployment_id>/submit/",
        test_user_view.TestSubmissionSubmitView.as_view(),
        name="submission_submit",
    ),  
    # 쪽지 시험 결과 조회
    path(
        "test/submissions/<int:submission_id>/result/",
        test_user_view.TestSubmissionResultView.as_view(),
        name="submission_result",
    ),  
    # admin
    # 쪽지 시험 응시 내역 전체 목록 조회
    path(
        "admin/test-submissions/",
        test_admin_view.AdminTestSubmissionsView.as_view(),
        name="admin_submission_List",
    ),  
     # 쪽지 시험 응시 내역 상세 조회
    path(
        "admin/test-submissions/<int:submission_id>",
        test_admin_view.AdminTestSubmissionDetailView.as_view(),
        name="admin_submission_detail",
    ), 
    # 쪽지 시험 응시 내역 삭제
    path(
        "admin/test-submissions/<int:submission_id>/delete",
        test_admin_view.AdminTestSubmissionDeleteView.as_view(),
        name="admin_submission_delete",
    ),  
    path("admin/tests/<int:test_id>/delete/", AdminTestDeleteAPIView.as_view(), name="admin-test-delete"),
    path("admin/tests/<int:test_id>/update/", AdminTestUpdateAPIView.as_view(), name="admin-test-update"),
    path("admin/tests/<int:test_id>/", AdminTestDetailAPIView.as_view(), name="test-detail"),
    path("admin/tests/", AdminTestListView.as_view(), name="admin-test-list"),
    path("admin/tests/create", AdminTestCreateAPIView.as_view(), name="test-create"),
]
