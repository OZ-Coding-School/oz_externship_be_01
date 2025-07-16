from rest_framework.exceptions import ValidationError


def get_questions_snapshot_from_submission(submission):
    return submission.deployment.questions_snapshot_json


def get_questions_snapshot_from_deployment(deployment):
    return deployment.questions_snapshot_json


def validate_answers_json_format(answers_json, snapshot=None):
    if not isinstance(answers_json, dict):
        raise ValidationError("answers_json은 딕셔너리 형식이어야 합니다.")
    if snapshot:
        question_ids = {str(q.get("id")) for q in snapshot}
        for key in answers_json.keys():
            if key not in question_ids:
                raise ValidationError(f"등록되지 않은 문제 ID가 포함되어 있습니다: {key}")


def is_correct(submitted_answer, correct_answer):
    return submitted_answer == correct_answer


# 총 점수
def calculate_total_score(answers_json, questions_snapshot):
    total = 0
    for question in questions_snapshot:
        question_id = question.get("id")
        correct_answer = question.get("answer")
        point = question.get("point")

        submitted_answer_list = answers_json.get(str(question_id), [])
        submitted_answer = submitted_answer_list[0] if submitted_answer_list else None

        if is_correct(submitted_answer, correct_answer):
            total += point
    return total


# 맞은 문제 수
def calculate_correct_count(answers_json, questions_snapshot):
    count = 0
    for question in questions_snapshot:
        question_id = question.get("id")
        correct_answer = question.get("answer")

        submitted_answer_list = answers_json.get(str(question_id), [])
        submitted_answer = submitted_answer_list[0] if submitted_answer_list else None

        if is_correct(submitted_answer, correct_answer):
            count += 1
    return count
