from django.urls import path

from apps.qna.views.answers_views import (
    AdoptAnswerView,
    AnswerCommentCreateView,
    AnswerCreateView,
    AnswerUpdateView,
)

urlpatterns = [
    # answer
    path("questions/<int:question_id>/answers/", AnswerCreateView.as_view()),
    path("questions/<int:question_id>/answers/<int:answer_id>/", AnswerUpdateView.as_view()),
    path("questions/<int:question_id>/answers/<int:answer_id>/adopt/", AdoptAnswerView.as_view()),
    path("questions/answers/<int:answer_id>/comments/", AnswerCommentCreateView.as_view()),
]
