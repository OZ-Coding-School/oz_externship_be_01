from io import BytesIO

import PIL.Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.community.models import Post, PostCategory

User = get_user_model()


def create_test_image():
    image = PIL.Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")


class AdminPostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            email="admin@test.com",
            name="정승원",
            nickname="seoungwon",
            phone_number="01099998888",
            password="adminpass",
            role="ADMIN",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.category = PostCategory.objects.create(name="카테고리")
        self.attachment = SimpleUploadedFile(
            "test.txt", "첨부파일 내용입니다.".encode("utf-8"), content_type="text/plain"
        )
        self.image = create_test_image()
        self.post = Post.objects.create(title="기존 게시글", content="본문", category=self.category, author=self.admin)

    def test_admin_post_list(self):
        url = reverse("admin-posts-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post.id, [p["id"] for p in response.json()["results"]])

    def test_admin_post_detail(self):
        url = reverse("admin-post-detail", kwargs={"post_id": self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.post.id)

    def test_admin_post_update(self):
        url = reverse("admin-post-update", kwargs={"post_id": self.post.id})
        data = {
            "title": "수정된 제목",
            "content": "수정된 내용",
            "category_id": self.category.id,
            "attachments": [self.attachment],
            "images": [self.image],
        }
        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "수정된 제목")

    def test_admin_post_delete(self):
        url = reverse("admin-post-delete", kwargs={"post_id": self.post.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_admin_post_toggle_visibility(self):
        self.assertTrue(self.post.is_visible)
        url = reverse("admin-post-toggle-visibility", kwargs={"post_id": self.post.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_visible)

    def test_admin_notice_create(self):
        url = reverse("admin-notice")
        data = {
            "title": "공지입니다",
            "content": "공지 내용",
            "is_notice": True,
            "is_visible": True,
            "attachments": [self.attachment],
            "images": [self.image],
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(title="공지입니다", is_notice=True).exists())
