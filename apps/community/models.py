from django.conf import settings
from django.db import models


# 카테고리
class PostCategory(models.Model):
    name = models.CharField(max_length=20)
    status = models.BooleanField(default=True)  # 사용 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "post_categories"

    def __str__(self) -> str:
        return self.name


# 게시글
class Post(models.Model):
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=50)
    content = models.TextField()
    view_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)  # 게시글 노출 여부
    is_notice = models.BooleanField(default=False)  # 공지 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"

    def __str__(self) -> str:
        return f"[{self.id}] {self.title}"


# 게시글 첨부 파일
class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments")
    file_url = models.URLField()  # 파일 URL (외부 저장소 경로)
    file_name = models.CharField(max_length=50)  # 원본 파일명

    class Meta:
        db_table = "post_attachments"

    def __str__(self) -> str:
        return self.file_name


# 게시글 이미지 파일
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")  # 삽입된 게시글
    img_url = models.TextField()  # 이미지 경로(URL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "post_images"

    def __str__(self) -> str:
        return f"Image for Post {self.post.id}"


# 댓글
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")  # 댓글 단 게시글
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_comments"
    )  # 댓글 작성자
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"

    def __str__(self) -> str:
        return f"{self.author} - {self.content[:20]}"


# 댓글 태그
class CommentTags(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="tags")  # 태그된 댓글
    tagged_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tagged_in_comments"
    )  # 태그된 사용자
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comment_tags"

    def __str__(self) -> str:
        return f"Tag: {self.tagged_user} in Comment {self.comment.id}"


# 좋아요 기능
class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")  # 좋아요한 게시글
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes"
    )  # 좋아요 누른 사용자
    is_liked = models.BooleanField(default=True)  # 현재 좋아요 상태 (취소/복원 고려)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "post_likes"
        unique_together = ("post", "user")

    def __str__(self) -> str:
        return f"{self.user} → {self.post} ({'Liked' if self.is_liked else 'Unliked'})"
