from django.urls import path

from apps.community.views.admin.comment_views import AdminCommentDeleteAPIView
from apps.community.views.admin.notice_views import NoticeCreateAPIView

urlpatterns = [
    path("admin/notices/", NoticeCreateAPIView.as_view(), name="admin-notice"),
    path("comments/<int:comment_id>/", AdminCommentDeleteAPIView.as_view()),
]  # 공지사항
