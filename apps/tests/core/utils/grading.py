from rest_framework.exceptions import ValidationError

from apps.tests.models import TestQuestion


def validate_answers_json_format(answers_json):
    if not isinstance(answers_json, dict):
        raise ValidationError("answers_json은 딕셔너리 형식이어야 합니다.")


def is_correct(submitted_answer, correct_answer):
    return submitted_answer == correct_answer


# 총 점수
def calculate_total_score(answers_json):
    total = 0
    question_ids = [int(k) for k in answers_json.keys() if k.isdigit()]
    questions = TestQuestion.objects.filter(id__in=question_ids)
    question_map = {q.id: q for q in questions}

    for qid_str, submitted_answer in answers_json.items():
        qid = int(qid_str)
        question = question_map.get(qid)
        if not question:
            continue

        if is_correct(submitted_answer, question.answer):
            total += question.point

    return total


# 맞은 문제 수
def calculate_correct_count(answers_json):
    count = 0
    question_ids = [int(k) for k in answers_json.keys() if k.isdigit()]
    questions = TestQuestion.objects.filter(id__in=question_ids)
    question_map = {q.id: q for q in questions}

    for qid_str, submitted_answer in answers_json.items():
        qid = int(qid_str)
        question = question_map.get(qid)
        if not question:
            continue

        if is_correct(submitted_answer, question.answer):
            count += 1

    return count
