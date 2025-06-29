from typing import Any, Dict  # Dict 임포트 추가

from rest_framework import serializers

from apps.courses.models import Course, Subject


# --- SubjectListSerializer (목록 조회용) ---
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
            "thumbnail_img_url",  # 목록 조회에도 포함
        ]
        read_only_fields = fields


# --- SubjectSerializer (과목 등록용 - POST 요청) ---
class SubjectSerializer(serializers.ModelSerializer[Subject]):
    """
    과목 등록 (POST) API를 위한 시리얼라이저.
    입력 필드와 생성 후 반환될 필드를 정의합니다.
    """

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="course",
        write_only=True,
        help_text="이 과목이 속할 과정의 고유 ID (입력 전용)",
    )

    course_name = serializers.CharField(source="course.name", read_only=True, help_text="과목이 속한 과정의 이름")

    # POST 요청 시 파일을 받을 필드 (이름 변경: thumbnail_img_file)
    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (POST/PATCH 시 사용)",  # help_text도 통일
    )

    # 응답 시 URL을 반환할 필드 (기존 모델 필드를 그대로 사용)
    thumbnail_img_url = serializers.URLField(
        read_only=True,
        help_text="썸네일 이미지 URL (응답 시 반환)",
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "course_id",
            "course_name",
            "title",
            "number_of_hours",
            "number_of_days",  # 순서 변경
            "status",
            "created_at",
            "updated_at",
            "thumbnail_img_file",  # 파일 입력을 위한 필드 (이름 변경)
            "thumbnail_img_url",  # URL 출력을 위한 필드
        ]
        # 위 필드들도 이제 read_only로 설정합니다.
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    # validated_data의 타입 힌트를 Dict[str, Any]로 수정 (Mypy 오류 해결)
    def create(self, validated_data: Dict[str, Any]) -> Subject:
        # 'thumbnail_img_file'은 write_only 필드이므로, validated_data에서 제거하고 처리합니다.
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)

        if thumbnail_img_file:
            # 실제 S3 업로드 로직이 여기에 들어갑니다.
            # 지금은 mock URL을 사용합니다.
            validated_data["thumbnail_img_url"] = f"http://mockserver.com/media/{thumbnail_img_file.name}"

        return super().create(validated_data)


# --- SubjectDetailSerializer (상세 조회용 - GET 요청) ---
class SubjectDetailSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 조회 API를 위한 시리얼라이저.
    GET 요청 시 특정 과목의 상세 정보를 정의합니다.
    """

    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "title",
            "thumbnail_img_url",
            "course_name",
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# --- SubjectUpdateSerializer (상세 수정용 - PATCH 요청) ---
class SubjectUpdateSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 수정 API를 위한 시리얼라이저.
    PATCH 요청 시 입력 및 응답 필드를 정의합니다.
    """

    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    # PATCH 요청 시 파일을 받을 필드 (이름 변경: thumbnail_img_file)
    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (POST/PATCH 시 사용)",  # help_text도 통일
    )

    # 응답 시 URL을 반환할 필드 (read_only)
    thumbnail_img_url = serializers.URLField(
        read_only=True,
        help_text="썸네일 이미지 URL (응답 시 반환)",
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "course_name",
            "title",
            "thumbnail_img_url",  # URL 출력을 위한 필드
            "thumbnail_img_file",  # 파일 입력을 위한 필드 (이름 변경)
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        # 위 필드들도 이제 read_only로 설정합니다.
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    # validated_data의 타입 힌트를 Dict[str, Any]로 수정 (Mypy 오류 해결)
    def update(self, instance: Subject, validated_data: Dict[str, Any]) -> Subject:
        # 'thumbnail_img_file'은 write_only 필드이므로, validated_data에서 처리합니다.
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)

        if thumbnail_img_file:
            # 실제 파일 업로드 로직이 여기에 들어갑니다.
            # 지금은 mock URL을 사용합니다.
            instance.thumbnail_img_url = f"http://mockserver.com/media/updated_{thumbnail_img_file.name}"

        return super().update(instance, validated_data)
