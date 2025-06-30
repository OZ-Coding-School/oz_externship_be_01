from django.db import models

from apps.users.models import User


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


##########################################################################################
class ChatbotSession(models.Model):
    STATUS_CHOICES = (
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("rejected", "Rejected"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chatbot_sessions",
    )
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True, related_name="chatbot_sessions"
    )
    socket_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="connected")
    rejection_reason = models.CharField(max_length=255, null=True, blank=True)
    chat_count = models.PositiveIntegerField(default=0)  # 비로그인 유저 2회까지 허용 조건
    is_waiting_reply = models.BooleanField(default=False)  # True일 경우 비활성화 상태로 처리 # 🤔
    created_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Session {self.id} - {self.status}"

    class Meta:
        db_table = "chatbot_sessions"
        ordering = ["-created_at"]


class ChatbotMessage(models.Model):
    SENDER_CHOICES = (
        ("user", "User"),
        ("ai", "AI"),
    )

    session = models.ForeignKey(ChatbotSession, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    is_question_related = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender_type.capitalize()} Message in Session {self.session.id}"

    class Meta:
        db_table = "chatbot_messages"
        ordering = ["created_at"]


##########################################################################################


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
