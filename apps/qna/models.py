from django.db import models

from apps import users


class QuestionCategory(models.Model):
    CATEGORY_TYPES = [("major", "대분류"), ("middle", "중분류"), ("minor", "소분류"), ("general", "일반질문")]
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)
    name = models.CharField(max_length=15)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default="general")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "question_categories"


class Question(models.Model):
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, related_name="questions")
    author = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    title = models.CharField(max_length=50)
    content = models.TextField()
    view_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "questions"


class QuestionAIAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="ai_answers")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"AI Answer for {self.question.title}"

    class Meta:
        db_table = "question_ai_answers"


class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Image for {self.question.title}"

    class Meta:
        db_table = "question_images"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="answers")
    content = models.TextField()
    is_adopted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Answer by {self.author.nickname} for {self.question.title}"

    class Meta:
        db_table = "answers"


class AnswerImage(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="images")
    img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Image for Answer {self.answer.id} by {self.answer.author.nickname}"

    class Meta:
        db_table = "answer_images"


class AnswerComment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="answer_comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Comment by {self.author.nickname} on Answer {self.answer.id}"

    class Meta:
        db_table = "answer_comments"
