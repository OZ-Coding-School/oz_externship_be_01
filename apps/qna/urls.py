from django.urls import path

from .views.mock_views import (
    MockQuestionCreateView,
    MockQuestionDetailView,
    MockQuestionListView,
    MockQuestionUpdateView,
)

app_name = "qna"

urlpatterns = [
    # 질문 등록 (POST)
    path("api/v1/qna/questions/", MockQuestionCreateView.as_view()),
    # 질문 목록 조회 (GET)
    path("api/v1/qna/questions", MockQuestionListView.as_view()),
    # 질문 상세 조회 (GET)
    path("api/v1/qna/questions/<int:question_id>", MockQuestionDetailView.as_view()),
    # 질문 수정 (PATCH)
    path("api/v1/qna/questions/<int:question_id>", MockQuestionUpdateView.as_view()),
]
