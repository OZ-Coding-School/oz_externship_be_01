from apps.tests.models import TestSubmission
from apps.tests.serializers.test_submission_serializers import AdminTestListSerializer

# total_score 계산해서 각 객체에 속성으로 붙이기
def annotate_total_score(submissions: list[TestSubmission]) -> list[TestSubmission]:
    serializer = AdminTestListSerializer()
    for submission in submissions:
        submission.total_score = serializer.get_total_score(submission)  # type: ignore[attr-defined]
    return submissions


def sort_by_total_score(data: list[TestSubmission], ordering: str) -> list[TestSubmission]:
    # data = list(data)
    if ordering == "total_score_desc":
        data.sort(key=lambda x: x.total_score, reverse=True)  # type: ignore[attr-defined]
    elif ordering == "total_score_asc":
        data.sort(key=lambda x: x.total_score)  # type: ignore[attr-defined]
    else:
        # 기본 정렬은 created_at 기준 (내림차순)
        data.sort(key=lambda x: x.created_at, reverse=True)

    return data

# def sort_list(queryset, ordering: str):
#     if ordering == "score_desc":
#         return queryset.order_by("-score")
#     elif ordering == "score_asc":
#         return queryset.order_by("score")
#     return queryset.order_by("-created_at")
