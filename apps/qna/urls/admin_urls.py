from django.urls import path

from apps.qna.views.admin_views import (
    AdminAnswerDeleteView,
    AdminCategoryCreateView,
    AdminCategoryDeleteView,
    AdminCategoryListView,
    AdminQnADetailView,
    AdminQuestionDeleteView,
    AdminQuestionListView,
)

urlpatterns = [
    # 카테고리
    path("admin/categories/", AdminCategoryListView.as_view(), name="admin-category-list"),
    path("admin/categories/create/", AdminCategoryCreateView.as_view(), name="admin-category-create"),
    path("admin/categories/<int:category_id>/delete/", AdminCategoryDeleteView.as_view(), name="admin-category-delete"),
<<<<<<< Updated upstream
    path("admin/questions/<int:question_id>/delete/", AdminQuestionDeleteView.as_view(), name="admin-question-delete"),
    path("admin/questions/list/", AdminQuestionListView.as_view(), name="admin-question-list"),
=======
    # 질문
    path("admin/questions/", AdminQuestionListView.as_view(), name="admin-question-list"),
    path("admin/questions/<int:question_id>/", AdminQnADetailView.as_view(), name="admin-qna-detail"),
    path("admin/questions/<int:question_id>/delete/", AdminQuestionDeleteView.as_view(), name="admin-question-delete"),
    # 답변
>>>>>>> Stashed changes
    path("admin/answers/<int:answer_id>/delete/", AdminAnswerDeleteView.as_view(), name="admin-answer-delete"),
]
