from django.urls import path

from apps.community.views.user.comment_views import CommentListAPIView
from apps.community.views.admin.notice_views import NoticeCreateAPIView

urlpatterns = [
    path("posts/<int:post_id>/comments/", CommentListAPIView.as_view(), name="comment-list"),
    path("admin/notices/", NoticeCreateAPIView.as_view(), name="admin-notice"),  # 공지사항
]
