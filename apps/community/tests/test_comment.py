from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.community.models import Comment, CommentTags, Post, PostCategory

User = get_user_model()


class UserCommentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 유저 생성
        self.user = User.objects.create_user(
            email="user@test.com", name="일반유저", nickname="user1", phone_number="01012345678", password="userpass"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", name="다른유저", nickname="other1", phone_number="01087654321", password="otherpass"
        )
        self.tagged_user = User.objects.create_user(
            email="tagged@test.com", name="태그유저", nickname="tagged1", phone_number="01098765432", password="tagpass"
        )

        self.client.force_authenticate(user=self.user)

        # 게시글 + 댓글 생성
        self.category = PostCategory.objects.create(name="자유")
        self.post = Post.objects.create(
            title="테스트 게시글", content="게시글 내용", author=self.user, category=self.category
        )

        self.comment = Comment.objects.create(post=self.post, author=self.user, content="기존 댓글입니다")

    def test_comment_list(self):
        Comment.objects.create(post=self.post, author=self.user, content="댓글1")
        Comment.objects.create(post=self.post, author=self.user, content="댓글2")

        url = reverse("comment-list", kwargs={"post_id": self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)

    def test_create_comment(self):
        url = reverse("comment-create", kwargs={"post_id": self.post.id})
        data = {"content": "새 댓글입니다"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Comment.objects.filter(content="새 댓글입니다").exists())

    def test_create_comment_with_tag(self):
        url = reverse("comment-create", kwargs={"post_id": self.post.id})
        data = {"content": f"@{self.tagged_user.nickname} 댓글입니다"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.get(content__icontains=self.tagged_user.nickname)
        self.assertTrue(CommentTags.objects.filter(comment=comment, tagged_user=self.tagged_user).exists())

    def test_create_comment_empty_content_fail(self):
        url = reverse("comment-create", kwargs={"post_id": self.post.id})
        data = {"content": ""}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_update_own_comment(self):
        url = reverse("comment-update", kwargs={"comment_id": self.comment.id})
        data = {"content": "수정된 댓글"}
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "수정된 댓글")

    def test_update_comment_empty_content_fail(self):
        url = reverse("comment-update", kwargs={"comment_id": self.comment.id})
        data = {"content": ""}
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_update_other_users_comment_fail(self):
        comment_by_other = Comment.objects.create(post=self.post, author=self.other_user, content="남이 쓴 댓글")
        url = reverse("comment-update", kwargs={"comment_id": comment_by_other.id})
        data = {"content": "남의 댓글 수정 시도"}
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_delete_own_comment(self):
        url = reverse("comment-delete", kwargs={"comment_id": self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_other_users_comment_fail(self):
        comment_by_other = Comment.objects.create(post=self.post, author=self.other_user, content="남이 쓴 댓글")
        url = reverse("comment-delete", kwargs={"comment_id": comment_by_other.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
