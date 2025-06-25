from django.urls import path

from apps.community.views.admin.notice_views import NoticeCreateAPIView

urlpatterns = [
    path("admin/notices/", NoticeCreateAPIView.as_view(), name="admin-notice"),  # 공지사항
]
