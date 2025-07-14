from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.community.models import Post, PostCategory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserPostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='seoungwon@test.com',
            name='정승원',
            nickname='seoungwon',
            phone_number='01011112222',
            password='userpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.category = PostCategory.objects.create(name="자유 게시판")
        self.post = Post.objects.create(
            title='테스트 제목',
            content='테스트 내용',
            author=self.user,
            category=self.category
        )

    def test_user_post_list(self):
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["id"] == self.post.id for p in response.data["results"]))

    def test_user_post_detail(self):
        url = reverse('post-detail', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.post.id)

    def test_user_post_create(self):
        url = reverse('post-create')
        data = {
            "title": "새 게시글",
            "content": "내용입니다",
            "category_id": self.category.id
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(title="새 게시글").exists())

    def test_user_post_update(self):
        url = reverse('post-update', kwargs={'post_id': self.post.id})
        response = self.client.patch(url, {"title": "수정된 제목"}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "수정된 제목")

    def test_user_post_delete(self):
        url = reverse('user-post-delete', kwargs={'post_id': self.post.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())