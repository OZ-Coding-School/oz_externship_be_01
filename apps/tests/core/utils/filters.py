def filter_test_submissions(queryset, filters):
    subject = filters.get("subject_title")
    course = filters.get("course_title")
    generation = filters.get("generation_number")

    subject = subject.strip() if subject else None
    course = course.strip() if course else None
    generation = int(generation) if generation else None

    if subject:
        queryset = queryset.filter(deployment__test__subject__title__icontains=subject)
        print(queryset.count())
        print(list(queryset))
    if course:
        queryset = queryset.filter(deployment__generation__course__name__icontains=course)
    if generation:
        queryset = queryset.filter(deployment__generation__number=generation)

    return queryset
