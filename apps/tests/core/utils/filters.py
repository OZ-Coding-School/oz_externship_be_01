def filter_test_submissions(queryset, filters):
    subject = filters.get("subject_title")
    course = filters.get("course_title")
    generation = filters.get("generation_number")

    # 필요하면 strip()도 추가
    subject = subject.strip() if subject else None
    course = course.strip() if course else None
    generation = int(generation) if generation else None

    print("subject_title 값:", subject)
    print("course_title 값:", course)
    print("generation_number 값:", generation)


    if subject:
        queryset = queryset.filter(deployment__test__subject__title__icontains=subject)
        print(queryset.count())
        print(list(queryset))
    if course:
        queryset = queryset.filter(deployment__generation__course__name__icontains=course)
    if generation:
        queryset = queryset.filter(deployment__generation__number=generation)

    return queryset

    # # case 1: 과목만 있는 경우
    # if subject and not course and not generation:
    #     return queryset.filter(deployment__test__subject__title__icontains=subject)
    #
    # # case 2: 과정 + 기수만 있는 경우
    # if not subject and course and generation:
    #     return queryset.filter(
    #         deployment__generation__course__name__icontains=course,
    #         deployment__generation__number=generation
    #     )
    #
    # # case 3: 과목 + 과정 + 기수 모두 있는 경우
    # if subject and course and generation:
    #     return queryset.filter(
    #         deployment__test__subject__title__icontains=subject,
    #         deployment__generation__course__name__icontains=course,
    #         deployment__generation__number=generation
    #     )
    #
    # # case 4: 아무 조건도 없으면 전체 조회
    # return queryset

# 과목만 선택하는 경우 해당 과목에 응시한 모든 응시내역을 조회
# 과정 - 기수를 모두 선택하는 경우 응시내역 중 해당 과정 - 기수가 응시한 모든 응시내역을 조회
# 둘다 선택하는 경우 응시내역 중 해당 과목에 대해서 해당 과정 - 기수가 응시한 모든 응시내역을 조회


    # case 1: 과목만 있는 경우




