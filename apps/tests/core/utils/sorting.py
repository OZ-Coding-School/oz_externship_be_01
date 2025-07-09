from apps.tests.models import TestSubmission
from apps.tests.serializers.test_submission_serializers import (
    AdminTestSubmissionListSerializer,
)


def annotate_total_score(submissions: list[TestSubmission]) -> list[TestSubmission]:
    serializer = AdminTestSubmissionListSerializer()
    for submission in submissions:
        submission.total_score = serializer.get_total_score(submission)  # type: ignore[attr-defined]
    return submissions


def sort_by_total_score(data: list[TestSubmission], ordering: str) -> list[TestSubmission]:
    if ordering == "total_score_desc":
        data.sort(key=lambda x: x.total_score, reverse=True)  # type: ignore[attr-defined]
    elif ordering == "total_score_asc":
        data.sort(key=lambda x: x.total_score)  # type: ignore[attr-defined]
    else:
        # 기본 정렬: 내림차순
        data.sort(key=lambda x: x.created_at, reverse=True)

    return data
