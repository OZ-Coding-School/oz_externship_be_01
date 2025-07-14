import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.community.models import Post, PostCategory

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="seoungwon@test.com",
        name="정승원",
        nickname="seoungwon",
        phone_number="01011112222",
        password="userpass123",
    )


@pytest.fixture
def category(db):
    return PostCategory.objects.create(name="자유 게시판")


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def post(user, category):
    return Post.objects.create(title="테스트 제목", content="테스트 내용", author=user, category=category)


def test_user_post_list(api_client, post):
    url = reverse("post-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert any(p["id"] == post.id for p in response.data["results"])


def test_user_post_detail(api_client, post):
    url = reverse("post-detail", kwargs={"post_id": post.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == post.id


def test_user_post_create(api_client, category):
    url = reverse("post-create")
    data = {"title": "새 게시글", "content": "내용입니다", "category_id": category.id}
    response = api_client.post(url, data, format="multipart")
    assert response.status_code == status.HTTP_201_CREATED
    assert Post.objects.filter(title="새 게시글").exists()


def test_user_post_update(api_client, post):
    url = reverse("post-update", kwargs={"post_id": post.id})
    response = api_client.patch(url, {"title": "수정된 제목"}, format="multipart")
    assert response.status_code == status.HTTP_200_OK
    post.refresh_from_db()
    assert post.title == "수정된 제목"


def test_user_post_delete(api_client, post):
    url = reverse("user-post-delete", kwargs={"post_id": post.id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(id=post.id).exists()
