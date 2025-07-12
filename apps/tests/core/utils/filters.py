from apps.tests.models import TestSubmission


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


def filter_test_submissions_list(queryset, filters, student):
    course = filters.get("course_title")
    generation = filters.get("generation_number")
    submission_status = filters.get("submission_status")

    if course:
        queryset = queryset.filter(deployment__generation__course__name__icontains=course)
    if generation:
        queryset = queryset.filter(deployment__generation__number=generation)

    if submission_status and student:
        submitted_deployments = TestSubmission.objects.filter(student=student).values_list("deployment_id", flat=True)
        if submission_status == "completed":
            queryset = queryset.filter(deployment__id__in=submitted_deployments)
        elif submission_status == "not_submitted":
            queryset = queryset.exclude(deployment__id__in=submitted_deployments)

    return queryset
