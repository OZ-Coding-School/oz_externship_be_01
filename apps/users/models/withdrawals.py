from datetime import date, timedelta

from django.db import models

from apps.users.models.user import User


# 회원 탈퇴 2주후 삭제
def two_weeks_later() -> date:
    return date.today() + timedelta(days=14)


class Withdrawal(models.Model):
    class Reason(models.TextChoices):
        TOO_EXPENSIVE = "TOO_EXPENSIVE", "비쌈"
        NOT_SATISFIED = "NOT_SATISFIED", "불만족"
        ETC = "ETC", "기타"

    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name="withdrawal", null=True)
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reason_detail = models.TextField()
    due_date = models.DateField(default=two_weeks_later)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "withdrawals"

    def __str__(self) -> str:
        return f"{self.user.email} - {self.get_reason_display()}"  # type: ignore
