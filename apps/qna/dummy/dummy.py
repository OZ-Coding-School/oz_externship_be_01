from django.utils import timezone

from apps.qna.models import (
    Answer,
    AnswerComment,
    AnswerImage,
    Question,
    QuestionCategory,
    QuestionImage,
)
from apps.users.models import User

# 더미 데이터

DUMMY_USER = User(id=1, email="mock@example.com", nickname="oz_student", profile_image_url="/media/mock_user.png")
DUMMY_CATEGORY = []
DUMMY_QUESTIONS = []
DUMMY_QUESTION_IMAGES = []
DUMMY_ANSWERS = []
DUMMY_ANSWER_IMAGES = []
DUMMY_ANSWER_COMMENTS = []

# 1. 대분류 (parent 없음)
parent_category = QuestionCategory.objects.create(
    name="Python",
    parent=None,
    created_at=timezone.now(),
)
DUMMY_CATEGORY.append(parent_category)

# 2. 중분류 (대분류의 하위)
middle_category = QuestionCategory.objects.create(
    name="Django",
    parent=parent_category,  # 대분류를 parent로 지정
    created_at=timezone.now(),
)
DUMMY_CATEGORY.append(middle_category)

# 3. 소분류 (중분류의 하위)
sub_category = QuestionCategory.objects.create(
    name="typeerror",
    parent=middle_category,  # 중분류를 parent로 지정
    created_at=timezone.now(),
)
DUMMY_CATEGORY.append(sub_category)

# 질문
for i in range(1, 4):
    question = Question(
        id=i,
        title=f"샘플 질문 제목 {i}",
        content=f"샘플 질문 내용 {i}",
        author=DUMMY_USER,
        category=sub_category,
        created_at=timezone.now(),
    )
    DUMMY_QUESTIONS.append(question)

# 질문 이미지
for q in DUMMY_QUESTIONS:
    DUMMY_QUESTION_IMAGES.append(
        QuestionImage(id=1, question=q, img_url=f"/media/sample_1.png", created_at=timezone.now())
    )
    DUMMY_QUESTION_IMAGES.append(
        QuestionImage(id=2, question=q, img_url=f"/media/sample_2.png", created_at=timezone.now())
    )


for i, question in enumerate(DUMMY_QUESTIONS, start=1):
    # 답변 생성
    answer = Answer(
        id=i,
        question=question,
        author=DUMMY_USER,
        content=f"샘플 답변 내용 {i}",
        is_adopted=(i == 1),  # 첫 번째만 채택
        created_at=timezone.now(),
    )
    DUMMY_ANSWERS.append(answer)

    # 답변 이미지 2장 생성
    for j in range(1, 3):
        img = AnswerImage(
            answer=answer,
            img_url=f"/media/answer_sample{i}_{j}.png",
            created_at=timezone.now(),
        )
        DUMMY_ANSWER_IMAGES.append(img)
    # 답변 댓글 1개 생성
    comment = AnswerComment(
        answer=answer,
        author=DUMMY_USER,
        content=f"답변에 대한 샘플 댓글 {i}",
        created_at=timezone.now(),
    )
    DUMMY_ANSWER_COMMENTS.append(comment)
