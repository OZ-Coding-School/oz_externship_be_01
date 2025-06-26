from django.urls import path

from apps.qna.views.admin_views import (
    AdminAnswerDeleteView,
    AdminCategoryCreateView,
    AdminCategoryDeleteView,
    AdminQuestionDeleteView,
)

app_name = "qna"

urlpatterns = [
    path("admin/categories/create/", AdminCategoryCreateView.as_view(), name="admin-category-create"),
    path("admin/categories/delete/", AdminCategoryDeleteView.as_view(), name="admin-category-delete"),
    path("admin/questions/delete/", AdminQuestionDeleteView.as_view(), name="admin-question-delete"),
    path("admin/answers/delete/", AdminAnswerDeleteView.as_view(), name="admin-answer-delete"),
]
