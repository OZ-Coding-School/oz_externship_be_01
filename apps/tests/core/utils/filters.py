from django.db.models import Exists, OuterRef

from apps.tests.models import TestDeployment, TestSubmission


# 관리자 쪽지 시험 응시 내역 목록 조회 (과목, 과정, 기수 필터 포함)
def filter_test_submissions(queryset, filters):
    subject = filters.get("subject_title")
    course = filters.get("course_title")
    generation = filters.get("generation_number")

    subject = subject.strip() if subject else None
    course = course.strip() if course else None
    generation = int(generation) if generation else None

    if subject:
        queryset = queryset.filter(deployment__test__subject__title__icontains=subject)
    if course:
        queryset = queryset.filter(deployment__generation__course__name__icontains=course)
    if generation:
        queryset = queryset.filter(deployment__generation__number=generation)

    return queryset


# 사용자 쪽지 시험 목록 조회 (과정, 기수 필터 포함)
def filter_deployments_by_course_and_generation(queryset, filters):
    course = filters.get("course_title")
    generation = filters.get("generation_number")

    if course:
        queryset = queryset.filter(generation__course__name__icontains=course)
    if generation:
        queryset = queryset.filter(generation__number=generation)

    return queryset


# 사용자 쪽지 시험 목록 조회 (응시 상태: 응시완료, 미응시)
def filter_deployments_by_submission_status(queryset, student, submission_status):
    submitted_qs = TestSubmission.objects.filter(
        deployment=OuterRef("pk"),
        student=student,
    )

    annotated_qs = queryset.annotate(has_submitted=Exists(submitted_qs))

    if submission_status == "completed":
        filtered_qs = annotated_qs.filter(has_submitted=True)
    elif submission_status == "not_submitted":
        filtered_qs = annotated_qs.filter(has_submitted=False)
    else:
        filtered_qs = annotated_qs

    return filtered_qs.order_by("-created_at")
