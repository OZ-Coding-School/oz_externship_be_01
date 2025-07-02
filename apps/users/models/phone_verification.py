from django.db import models
from django.utils import timezone

class PhoneVerificationCode(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6, help_text="인증 코드")
    expires_at = models.DateTimeField(help_text="만료 시간")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone_number} - {self.code} (만료: {self.expires_at})"