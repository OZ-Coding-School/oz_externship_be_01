from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from apps.users.models.user import User


class CustomUserManager(BaseUserManager["User"]):
    def create_user(self, email: str, password: str, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields["is_staff"]:
            raise ValueError("superuser는 is_staff=True여야 합니다.")
        if not extra_fields["is_superuser"]:
            raise ValueError("superuser는 is_superuser=True여야 합니다.")

        return self.create_user(email, password, **extra_fields)
