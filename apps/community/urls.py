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
from apps.community.views.admin.post_views import (
    AdminPostDeleteView,
    AdminPostDetailView,
    AdminPostListView,
    AdminPostUpdateView,
    AdminPostVisibilityToggleView,
)
from apps.community.views.user.comment_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentListAPIView,
    CommentUpdateAPIView,
)
from apps.community.views.user.post_create_views import PostCreateAPIView
from apps.community.views.user.post_delete import PostDeleteAPIView
from apps.community.views.user.post_detail_views import UserPostDetailAPIView
from apps.community.views.user.post_like_views import (
    PostLikeFalseAPIView,
    PostLikeTrueAPIView,
)
from apps.community.views.user.post_list_views import PostListAPIView
from apps.community.views.user.post_views import UserPostUpdateView

urlpatterns = [
    # admin
    path("admin/categories/create/", AdminCommunityCategoryCreateAPIView.as_view(), name="admin_category_create"),
    path("admin/categories/", AdminCategoryListAPIView.as_view(), name="admin_category_list"),
    path(
        "admin/categories/<int:category_id>/",
        AdminCommunityCategoryDetailAPIView.as_view(),
        name="admin_category_detail",
    ),
    path(
        "admin/categories/<int:category_id>/rename/",
        AdminCategoryRenameAPIView.as_view(),
        name="admin_category_rename",
    ),
    path(
        "admin/community/category/<int:category_id>/on/", CategoryStatusOnAPIView.as_view(), name="category-status-on"
    ),
    path(
        "admin/community/category/<int:category_id>/off/",
        CategoryStatusOffAPIView.as_view(),
        name="category-status-off",
    ),
    path("admin/notices/", NoticeCreateAPIView.as_view(), name="admin-notice"),
    path("admin/posts/", AdminPostListView.as_view(), name="admin-posts-list"),
    path("admin/posts/<int:post_id>/", AdminPostDetailView.as_view(), name="admin-post-detail"),
    path("admin/posts/<int:post_id>/update/", AdminPostUpdateView.as_view(), name="admin-post-update"),
    path("admin/posts/<int:post_id>/delete/", AdminPostDeleteView.as_view(), name="admin-post-delete"),
    path(
        "admin/posts/<int:post_id>/visibility/",
        AdminPostVisibilityToggleView.as_view(),
        name="admin-post-toggle-visibility",
    ),
    path("admin/comments/<int:comment_id>/", AdminCommentDeleteAPIView.as_view(), name="admin-comment-delete"),
    # user
    path("posts/<int:post_id>/", UserPostDetailAPIView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/comments/create/", CommentCreateAPIView.as_view(), name="comment-create"),
    path("comments/<int:comment_id>/update/", CommentUpdateAPIView.as_view(), name="comment-update"),
    path("comments/<int:comment_id>/delete/", CommentDeleteAPIView.as_view(), name="comment-delete"),
    path("posts/<int:post_id>/comments/", CommentListAPIView.as_view(), name="comment-list"),
    path("posts/create/", PostCreateAPIView.as_view(), name="post-create"),
    path("posts/<int:post_id>/like/", PostLikeTrueAPIView.as_view(), name="post-like"),
    path("posts/<int:post_id>/unlike/", PostLikeFalseAPIView.as_view(), name="post-unlike"),
    path("posts/list", PostListAPIView.as_view(), name="post-list"),
    path("posts/<int:post_id>/update/", UserPostUpdateView.as_view(), name="post-update"),
    path("posts/<int:post_id>/delete/", PostDeleteAPIView.as_view(), name="post-delete"),
]
