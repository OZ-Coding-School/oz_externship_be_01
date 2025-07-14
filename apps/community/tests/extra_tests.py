import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.community.models import (
    Post, PostCategory, PostAttachment, PostImage, PostLike
)
from django.contrib.auth import get_user_model

User = get_user_model()



@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='user1@test.com',
        name='홍길동',
        nickname='testnick',
        phone_number='01011112222',
        password='testpass'
    )

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def category(db):
    return PostCategory.objects.create(name="자유 게시판")

@pytest.fixture
def post(user, category):
    return Post.objects.create(
        title="숨김 테스트용 게시글",
        content="내용입니다",
        category=category,
        author=user,
    )

def test_like_post(api_client, post, user):
    url = reverse("post-like", kwargs={"post_id": post.id})
    response = api_client.post(url)
    assert response.status_code == 200
    assert PostLike.objects.filter(post=post, user=user, is_liked=True).exists()

def test_unlike_post(api_client, post, user):
    api_client.post(reverse("post-like", kwargs={"post_id": post.id}))
    url = reverse("post-unlike", kwargs={"post_id": post.id})
    response = api_client.post(url)
    assert response.status_code == 200
    assert not PostLike.objects.filter(post=post, user=user, is_liked=True).exists()



def test_post_detail_includes_attachments_and_thumbnail(api_client, post):
    PostAttachment.objects.create(post=post, file_url="http://test.com/file1.pdf", file_name="file1.pdf")
    PostImage.objects.create(post=post, image_url="http://test.com/img.jpg", image_name="img.jpg")

    url = reverse('post-detail', kwargs={"post_id": post.id})
    response = api_client.get(url)
    data = response.data

    assert "attachments" in data
    assert "images" in data
    assert any(img["image_url"] for img in data["images"])
    if "thumbnail_image" in data:
        assert data["thumbnail_image"].startswith("http")


def test_hidden_post_detail_returns_error(api_client, post):
    post.is_visible = False
    post.save()

    url = reverse("post-detail", kwargs={"post_id": post.id})
    response = api_client.get(url)
    assert response.status_code == 404 or "블라인드" in response.data.get("detail", "")