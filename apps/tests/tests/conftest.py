import io
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.courses.models import Course, Subject
from apps.users.models import User


# DRF APIClient 인스턴스
@pytest.fixture
def api_client():
    return APIClient()


# 관리자 계정 생성
@pytest.fixture
def admin_user():
    user = User.objects.create_user(
        email="admin@example.com",
        password="password123!",
        role=User.Role.ADMIN,
        name="관리자테스트계정",
        nickname="adminnick",
        phone_number="01000000000",
    )
    return user


# 실제 Course 모델 필드 기준으로 Course 생성
@pytest.fixture
def course():
    course = Course.objects.create(
        name="테스트코스",
        tag="TC1",
        description="쪽지시험 CRUD API 테스트용 코스",
        thumbnail_img_url="https://example.com/test-course.png",
    )
    return course


# 실제 Subject 모델 필드 기준으로 Subject 생성 (Course와 연결)
@pytest.fixture
def subject(course):
    subject = Subject.objects.create(
        course=course,
        title="테스트과목",
        number_of_days=10,
        number_of_hours=20,
        thumbnail_img_url="https://example.com/test-subject.png",
        status=True,
    )
    return subject


# 테스트용 가상 썸네일 이미지 파일 생성
@pytest.fixture
def thumbnail_file():
    file_io = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="blue")
    image.save(file_io, format="PNG")
    file_io.seek(0)
    return SimpleUploadedFile(name="test_thumbnail.png", content=file_io.read(), content_type="image/png")


# 생성/수정/삭제 API 테스트 시 실제 S3 호출 방지
@pytest.fixture(autouse=True)
def mock_s3_upload_and_delete():
    with (
        patch("core.utils.s3_file_upload.S3Uploader.upload_file") as mock_upload,
        patch("core.utils.s3_file_upload.S3Uploader.delete_file") as mock_delete,
        patch("core.utils.s3_file_upload.S3Uploader.update_file") as mock_update,
    ):
        mock_upload.return_value = "https://fake-s3-bucket/test-thumbnail.png"
        mock_delete.return_value = True
        mock_update.return_value = "https://fake-s3-bucket/updated-thumbnail.png"

        def upload_side_effect(*args, **kwargs):
            print("[MOCK] S3Uploader.upload_file() 호출됨!")
            return "https://fake-s3-bucket/test-thumbnail.png"

        def delete_side_effect(*args, **kwargs):
            print("[MOCK] S3Uploader.delete_file() 호출됨!")
            return True

        def update_side_effect(*args, **kwargs):
            print("[MOCK] S3Uploader.update_file() 호출됨!")
            return "https://fake-s3-bucket/updated-thumbnail.png"

        mock_upload.side_effect = upload_side_effect
        mock_delete.side_effect = delete_side_effect
        mock_update.side_effect = update_side_effect

        yield mock_upload, mock_delete, mock_update
