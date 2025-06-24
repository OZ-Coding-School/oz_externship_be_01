from datetime import date

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.users.manager.user_manager import CustomUserManager


class User(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "어드민"
        GENERAL = "GENERAL", "일반회원"
        STUDENT = "STUDENT", "수강생"
        TA = "TA", "조교"  # Training_Assistant
        OM = "OM", "운영매니저"  # Operation_Manager
        LC = "LC", "러닝코치"  # Learning_Coach

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    birthday = models.DateField(default=date(2000, 1, 1))
    self_introduction = models.CharField(max_length=255, null=True)
    profile_image_url = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GENERAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
