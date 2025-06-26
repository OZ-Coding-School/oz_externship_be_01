from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=30, unique=True)
    tag = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255)
    thumbnail_img_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "courses"


class Generation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="generations")
    number = models.PositiveSmallIntegerField()
    max_student = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10)  # e.g., 'open', 'closed'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "number")
        db_table = "generations"

    def __str__(self) -> str:
        return f"{self.course.name} - {self.number}기"


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    title = models.CharField(max_length=30, unique=True)
    number_of_days = models.PositiveSmallIntegerField()
    number_of_hours = models.PositiveSmallIntegerField()
    thumbnail_img_url = models.URLField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.course.name} - {self.title}"

    class Meta:
        db_table = "subjects"


class EnrollmentRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE, related_name="enrollments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "generation")
        db_table = "enrollment_requests"

    def __str__(self) -> str:
        return f"{self.user.name} requested to enrollment in  {self.generation}"
