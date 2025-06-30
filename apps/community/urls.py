from django.urls import path

from apps.community.views.admin.category_views import (
    AdminCategoryListAPIView,
    AdminCategoryRenameAPIView,
    AdminCommunityCategoryCreateAPIView,
    AdminCommunityCategoryDetailAPIView,
    CategoryStatusOffAPIView,
    CategoryStatusOnAPIView,
)
from apps.community.views.admin.comment_views import AdminCommentDeleteAPIView
from apps.community.views.admin.notice_views import NoticeCreateAPIView
from apps.community.views.user.comment_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentListAPIView,
    CommentUpdateAPIView,
)

urlpatterns = [
    path(
        "admin/categories/<int:category_id>/",
        AdminCommunityCategoryDetailAPIView.as_view(),
        name="admin_category_detail",
    ),
    path("admin/notices/", NoticeCreateAPIView.as_view(), name="admin-notice"),
    path("comments/<int:comment_id>/", AdminCommentDeleteAPIView.as_view()),
    path("posts/<int:post_id>/comments/", CommentListAPIView.as_view(), name="comment-list"),
    path("posts/<int:post_id>/comments/create/", CommentCreateAPIView.as_view(), name="comment-create"),
    path("comments/<int:comment_id>/update/", CommentUpdateAPIView.as_view(), name="comment-update"),
    path("comments/<int:comment_id>/delete/", CommentDeleteAPIView.as_view(), name="comment-delete"),
    path(
        "admin/community/category/<int:category_id>/on/", CategoryStatusOnAPIView.as_view(), name="category-status-on"
    ),
    path(
        "admin/community/category/<int:category_id>/off/",
        CategoryStatusOffAPIView.as_view(),
        name="category-status-off",
    ),
    path("admin/categories/create/", AdminCommunityCategoryCreateAPIView.as_view(), name="admin_category_create"),
    path("admin/categories/", AdminCategoryListAPIView.as_view(), name="admin_category_list"),
    path(
        "admin/categories/<int:category_id>/rename/",
        AdminCategoryRenameAPIView.as_view(),
        name="admin_category_rename",
    ),
]
