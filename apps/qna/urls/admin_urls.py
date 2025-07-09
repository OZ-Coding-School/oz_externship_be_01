from django.urls import path

from apps.qna.views.admin_views import (
    AdminAnswerDeleteView,
    AdminCategoryCreateView,
    AdminCategoryDeleteView,
    AdminCategoryListView,
    AdminQnaDetailView,
    AdminQuestionDeleteView,
    AdminQuestionListView,
)

urlpatterns = [
    # admin
    path("admin/categories/create/", AdminCategoryCreateView.as_view(), name="admin-category-create"),
    path("admin/categories/list/", AdminCategoryListView.as_view(), name="admin-category-list"),
    path("admin/categories/delete/", AdminCategoryDeleteView.as_view(), name="admin-category-delete"),
    path("admin/questions/<int:question_id>/delete/", AdminQuestionDeleteView.as_view(), name="admin-question-delete"),
    path("admin/questions/list/", AdminQuestionListView.as_view(), name="admin-question-list"),
    path("admin/answers/<int:answer_id>/delete/", AdminAnswerDeleteView.as_view(), name="admin-answer-delete"),
    path("admin/qna/<int:question_id>/detail/", AdminQnaDetailView.as_view(), name="admin-qna-detail"),
]
