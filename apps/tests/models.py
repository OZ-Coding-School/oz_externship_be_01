from django.db import models
from django.db.models import PositiveSmallIntegerField


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
    # 기존 전역 상수 QUESTION_TYPE_CHOICES 제거하고 모델 내부 TextChoices로 변경
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE_SINGLE = "multiple_choice_single", "객관식 단일 선택"
        MULTIPLE_CHOICE_MULTI = "multiple_choice_multi", "객관식 다중 선택"
        OX = "ox", "O,X 퀴즈"
        ORDERING = "ordering", "순서 정렬"
        FILL_IN_BLANK = "fill_in_blank", "빈칸 채우기"
        SHORT_ANSWER = "short_answer", "주관식 단답형"

    # ERD 기준: test_id
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=255)  # 문제 제목/내용
    prompt = models.TextField(null=True, blank=True)  # 문제 지문
    blank_count = models.PositiveSmallIntegerField(null=True, blank=True)  # 빈칸 문제일 경우 빈칸 수
    options_json = models.TextField(null=True, blank=True)  # 객관식/순서정렬 문제 보기를 JSON으로 저장
    # 기존 choices=QUESTION_TYPE_CHOICES → choices=QuestionType.choices로 변경
    type = models.CharField(
        max_length=50, choices=QuestionType.choices
    )  # 문제 유형 (객관식 단일/다중/순서/빈칸/주관식 등 대응)
    answer = models.JSONField()  # 배점
    point = models.PositiveSmallIntegerField()  # 해설
    explanation = models.TextField()  # 해설
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_questions"


class TestDeployment(models.Model):
    # 기존 전역 상수 TEST_STATUS_CHOICES 제거하고 모델 내부 TextChoices로 변경
    class TestStatus(models.TextChoices):
        ACTIVATED = "Activated", "활성화"
        DEACTIVATED = "Deactivated", "비활성화"

    # ERD 기준: generation_id
    generation = models.ForeignKey("courses.Generation", on_delete=models.CASCADE, related_name="test_deployments")
    # ERD 기준: test_id
    test = models.ForeignKey(
        Test,
        on_delete=models.SET_NULL,  # 기존 CASCADE → SET_NULL로 변경
        null=True,  # SET_NULL을 위해 필드 null 허용 필요 -> 배포 담당에게 전달
        related_name="deployments",
    )
    duration_time = models.PositiveSmallIntegerField(default=60)
    access_code = models.CharField(max_length=64)
    open_at = models.DateTimeField()
    close_at = models.DateTimeField()
    questions_snapshot_json = models.JSONField()
    # 기존 choices=TEST_STATUS_CHOICES → choices=TestStatus.choices로 변경
    status = models.CharField(max_length=50, choices=TestStatus.choices, default=TestStatus.ACTIVATED)
    question_count = PositiveSmallIntegerField(default=0)
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
    score = models.PositiveSmallIntegerField(default=0)
    correct_count = PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_submissions"
