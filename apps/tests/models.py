from django.db import models

# 문제 유형 enum
QUESTION_TYPE_CHOICES = [
    ("multiple_choice", "객관식"),
    ("ox", "O,X 퀴즈"),
    ("ordering", "순서 정렬"),
    ("fill_in_blank", "빈칸 채우기"),
]

# 배포 상태 enum
TEST_STATUS_CHOICES = [
    ("Activated", "활성화"),
    ("Deactivated", "비활성화"),
]


class Test(models.Model):
    # ERD 기준: subject_id
    subject = models.ForeignKey("courses.Subject", on_delete=models.CASCADE, related_name="tests")
    title = models.CharField(max_length=50)
    thumbnail_img_url = models.CharField(max_length=255, default="default_img_url")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tests"

    def __str__(self) -> str:
        return self.title


class TestQuestion(models.Model):
    # ERD 기준: test_id
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.PositiveSmallIntegerField(null=True, blank=True)
    options_json = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    answer = models.JSONField()
    point = models.PositiveSmallIntegerField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_questions"


class TestDeployment(models.Model):
    # ERD 기준: generation_id
    generation = models.ForeignKey("courses.Generation", on_delete=models.CASCADE, related_name="test_deployments")
    # ERD 기준: test_id
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="deployments")
    duration_time = models.PositiveSmallIntegerField(default=60)
    access_code = models.CharField(max_length=64)
    open_at = models.DateTimeField()
    close_at = models.DateTimeField()
    questions_snapshot_json = models.JSONField()
    status = models.CharField(max_length=50, choices=TEST_STATUS_CHOICES, default="Activated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_deployments"


class TestSubmission(models.Model):
    # ERD 기준: student_id
    student = models.ForeignKey("users.PermissionsStudent", on_delete=models.CASCADE, related_name="test_submissions")
    # ERD 기준: student_id
    student = models.ForeignKey("users.PermissionsStudent", on_delete=models.CASCADE, related_name="test_submissions")
    # ERD 기준: deployment_id
    deployment = models.ForeignKey(TestDeployment, on_delete=models.CASCADE, related_name="submissions")
    started_at = models.DateTimeField()
    cheating_count = models.PositiveSmallIntegerField(default=0)
    answers_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_submissions"
