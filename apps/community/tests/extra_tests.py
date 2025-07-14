from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.community.models import (
    Post, PostCategory, PostAttachment, PostImage, PostLike
)
from django.contrib.auth import get_user_model

User = get_user_model()


class PostExtraTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user1@test.com',
            name='정승원',
            nickname='seoungwon',
            phone_number='01011112222',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.category = PostCategory.objects.create(name="자유 게시판")
        self.post = Post.objects.create(
            title="숨김 테스트용 게시글",
            content="내용입니다",
            category=self.category,
            author=self.user,
        )

    def test_like_post(self):
        url = reverse("post-like", kwargs={"post_id": self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PostLike.objects.filter(post=self.post, user=self.user, is_liked=True).exists())

    def test_unlike_post(self):
        self.client.post(reverse("post-like", kwargs={"post_id": self.post.id}))
        url = reverse("post-unlike", kwargs={"post_id": self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PostLike.objects.filter(post=self.post, user=self.user, is_liked=True).exists())

    def test_post_detail_includes_attachments_and_thumbnail(self):
        PostAttachment.objects.create(post=self.post, file_url="http://test.com/file1.pdf", file_name="file1.pdf")
        PostImage.objects.create(post=self.post, image_url="http://test.com/img.jpg", image_name="img.jpg")

        url = reverse('post-detail', kwargs={"post_id": self.post.id})
        response = self.client.get(url)
        data = response.data

        self.assertIn("attachments", data)
        self.assertIn("images", data)
        self.assertTrue(any(img["image_url"] for img in data["images"]))
        if "thumbnail_image" in data:
            self.assertTrue(data["thumbnail_image"].startswith("http"))

    def test_hidden_post_detail_returns_error(self):
        self.post.is_visible = False
        self.post.save()
        url = reverse("post-detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)
        self.assertIn(response.status_code, [404])
        self.assertIn("블라인드", response.data.get("detail", ""))