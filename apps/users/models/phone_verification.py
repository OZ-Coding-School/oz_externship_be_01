from django.db import models


class PhoneVerificationCode(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "phone_verification_code"
