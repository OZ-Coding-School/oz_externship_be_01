from django.db import models

# 문제 유형 enum
QUESTION_TYPE_CHOICES = [
    ("multiple_choice_single", "객관식 단일 선택"),
    ("multiple_choice_multi", "객관식 다중 선택"),
    ("ox", "O,X 퀴즈"),
    ("ordering", "순서 정렬"),
    ("fill_in_blank", "빈칸 채우기"),
    ("short_answer", "주관식 단답형"),
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
    question = models.CharField(max_length=255)  # 문제 제목/내용
    prompt = models.TextField(null=True, blank=True)  # 문제 지문
    blank_count = models.PositiveSmallIntegerField(null=True, blank=True)  # 빈칸 문제일 경우 빈칸 수
    options_json = models.TextField(null=True, blank=True)  # 객관식/순서정렬 문제 보기를 JSON으로 저장
    type = models.CharField(
        max_length=50, choices=QUESTION_TYPE_CHOICES
    )  # 정답 (단일/다중/순서/빈칸/주관식 모두 대응 가능)
    answer = models.JSONField()  # 배점
    point = models.PositiveSmallIntegerField()  # 해설
    explanation = models.TextField()  # 해설
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

    # ERD 기준: deployment_id
    deployment = models.ForeignKey(TestDeployment, on_delete=models.CASCADE, related_name="submissions")
    started_at = models.DateTimeField()
    cheating_count = models.PositiveSmallIntegerField(default=0)
    answers_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_submissions"
