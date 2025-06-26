from django.db import models


class StudentEnrollmentRequest(models.Model):
    class EnrollmentStatus(models.TextChoices):
        PENDING = "PENDING", "대기"
        APPROVED = "APPROVED", "승인"
        REJECTED = "REJECTED", "거절"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="enrollment_requests")
    generation = models.ForeignKey("courses.Generation", on_delete=models.CASCADE, related_name="enrollment_requests")
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.PENDING)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_enrollment_request"
        ordering = ["-created_at"]
