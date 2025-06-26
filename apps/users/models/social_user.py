from django.db import models
from apps.users.models import User

class SocialUser(models.Model):
    class Provider(models.TextChoices):
        KAKAO = "KAKAO", "카카오"
        NAVER = "NAVER", "네이버"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=10, choices=Provider.choices)
    provider_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_users"
        unique_together = ("provider", "provider_id")  # 유니크로 묶어서 동일한 소셜 계정 중복 방지

    def __str__(self) -> str:
        return f"{self.user.email} - {self.provider}"