from django.urls import path


from apps.qna.views.answers_views import (
    AdoptAnswerView,
    AnswerCommentCreateView,
    AnswerCreateView,
    AnswerUpdateView
)

from apps.qna.views.admin_views import (
    AdminAnswerDeleteView,
    AdminCategoryCreateView,
    AdminCategoryDeleteView,
    AdminQuestionDeleteView,
)

from apps.qna.views.questions_views import (
    QuestionCreateView,
    QuestionDetailView,
    QuestionListView,
    QuestionUpdateView,
)

urlpatterns = [

    # questions
    path("questions/", QuestionListView.as_view(), name="question-list"),
    path("questions/create/", QuestionCreateView.as_view(), name="question-create"),
    path("questions/<int:question_id>/", QuestionDetailView.as_view(), name="question-detail"),
    path("questions/<int:question_id>/update/", QuestionUpdateView.as_view(), name="question-update"),
    # answer
    path("questions/<int:question_id>/answers/", AnswerCreateView.as_view()),
    path("questions/<int:question_id>/answers/<int:answer_id>/", AnswerUpdateView.as_view()),
    path("questions/<int:question_id>/answers/<int:answer_id>/adopt/", AdoptAnswerView.as_view()),
    path("questions/answers/<int:answer_id>/comments/", AnswerCommentCreateView.as_view()),
    # admin
    path("admin/categories/create/", AdminCategoryCreateView.as_view(), name="admin-category-create"),
    path("admin/categories/delete/", AdminCategoryDeleteView.as_view(), name="admin-category-delete"),
    path("admin/questions/delete/", AdminQuestionDeleteView.as_view(), name="admin-question-delete"),
    path("admin/answers/delete/", AdminAnswerDeleteView.as_view(), name="admin-answer-delete"),
]