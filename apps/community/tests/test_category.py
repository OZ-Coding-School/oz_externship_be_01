from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.community.models import PostCategory

User = get_user_model()


class AdminCategoryTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@test.com",
            name="관리자",
            nickname="admin1",
            phone_number="01012345678",
            password="adminpass",
            role="ADMIN",
        )
        self.client.force_authenticate(user=self.admin)

        self.category = PostCategory.objects.create(name="초기카테고리", status=True)

    def test_category_create(self):
        url = reverse("admin_category_create")
        data = {"name": "새 카테고리", "status": True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201, msg=response.json())
        self.assertTrue(PostCategory.objects.filter(name="새 카테고리").exists())

    def test_category_list(self):
        url = reverse("admin_category_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_category_detail(self):
        url = reverse("admin_category_detail", kwargs={"category_id": self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.category.id)

    def test_category_rename(self):
        url = reverse("admin_category_rename", kwargs={"category_id": self.category.id})
        data = {"name": "수정된 카테고리"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "수정된 카테고리")

    def test_category_delete(self):
        url = reverse("admin_category_detail", kwargs={"category_id": self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(PostCategory.objects.filter(id=self.category.id).exists())

    def test_category_status_on(self):
        self.category.status = False
        self.category.save()

        url = reverse("category-status-on", kwargs={"category_id": self.category.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertTrue(self.category.status)

    def test_category_status_off(self):
        self.category.status = True
        self.category.save()

        url = reverse("category-status-off", kwargs={"category_id": self.category.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertFalse(self.category.status)
