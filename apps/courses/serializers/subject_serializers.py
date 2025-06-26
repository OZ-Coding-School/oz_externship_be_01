# apps/courses/serializers/subject_serializer.py

from rest_framework import serializers

from apps.courses.models import Course, Subject  # 정의한 모델 임포트


# --- SubjectListSerializer (목록 조회용) ---
# 이곳을 수정합니다: serializers.ModelSerializer[Subject]
class SubjectListSerializer(serializers.ModelSerializer[Subject]):
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름")

    class Meta:
        model = Subject
        fields = [
            "id",
            "title",
            "number_of_days",
            "number_of_hours",
            "course_name",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# --- SubjectSerializer (과목 등록용 - POST 요청) ---
# 이곳을 수정합니다: serializers.ModelSerializer[Subject]
class SubjectSerializer(serializers.ModelSerializer[Subject]):
    """
    과목 등록 (POST) API를 위한 시리얼라이저.
    입력 필드와 생성 후 반환될 필드를 정의합니다.
    """

    # 요청 본문에서 'course_id'를 받아 'course' ForeignKey 필드에 매핑합니다.
    # write_only=True로 설정하여 이 필드가 응답에는 포함되지 않음을 명시합니다.
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True, help_text="이 과목이 속할 고유 ID (입력 전용)"
    )

    # 응답에 'course_name'을 포함시키기 위한 필드입니다.
    # read_only=True로 설정하여 입력 시에는 사용되지 않음을 명시합니다.
    # source='course.name'을 통해 관련 Course 모델의 'name'을 가져옵니다.
    course_name = serializers.CharField(source="course.name", read_only=True, help_text="과목이 속한 과정의 이름")

    class Meta:
        model = Subject
        # API 명세의 요청 본문 필드와 성공 응답 필드에 맞춥니다.
        fields = [
            "id",
            "course_id",  # 입력 필드. write_only=True이므로 응답에는 포함되지 않습니다.
            "course_name",  # 응답 필드. read_only=True이므로 입력으로는 사용되지 않습니다.
            "title",
            "thumbnail_img_url",
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        # id, created_at, updated_at, course_name은 읽기 전용으로 설정합니다.
        read_only_fields = ["id", "created_at", "updated_at", "course_name"]


# --- SubjectDetailSerializer (상세 조회용 - GET 요청) ---
# 이곳을 수정합니다: serializers.ModelSerializer[Subject]
class SubjectDetailSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 조회 API를 위한 시리얼라이저.
    GET 요청 시 특정 과목의 상세 정보를 정의합니다.
    """

    # 'course_name' 필드는 관련 Course 모델에서 'name' 필드를 가져옵니다.
    # API 명세의 응답 예시에서 'course_name'이 문자열로 제시되었으므로, StringField를 사용합니다.
    # (명세의 필드명-타입 설명에서는 BIGINT로 되어 있으나, 이는 오기일 가능성이 높습니다.)
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    class Meta:
        model = Subject
        # API 명세의 성공 응답 필드와 일치시킵니다.
        fields = [
            "id",
            "title",
            "thumbnail_img_url",
            "course_name",  # 새로 추가된 과정명 필드
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        # 모든 필드는 읽기 전용으로 설정합니다.
        read_only_fields = fields


# --- SubjectUpdateSerializer (상세 수정용 - PATCH 요청) ---
# 이곳을 수정합니다: serializers.ModelSerializer[Subject]
class SubjectUpdateSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 수정 API를 위한 시리얼라이저.
    PATCH 요청 시 입력 및 응답 필드를 정의합니다.
    """

    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    class Meta:
        model = Subject
        # API 명세의 요청 본문 필드와 성공 응답 필드에 맞춥니다.
        # PATCH 요청 시 모든 필드는 선택 사항이므로, 기본 동작으로 충분합니다.
        fields = [
            "id",
            "course_name",
            "title",
            "thumbnail_img_url",
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        # id, 생성일시, 수정일시, course 필드는 읽기 전용입니다.
        read_only_fields = ["id", "created_at", "updated_at"]
