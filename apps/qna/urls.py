from django.urls import path

from apps.qna.views.answers_views import (
    AdoptAnswerView,
    AnswerCommentCreateView,
    AnswerCreateView,
    AnswerUpdateView,
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
]
