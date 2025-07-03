from typing import Any, Dict

from rest_framework import serializers

from apps.courses.models import Course, Subject


# --- SubjectListSerializer (목록 조회용) ---
class SubjectListSerializer(serializers.ModelSerializer[Subject]):
    id = serializers.IntegerField(read_only=True)
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
            "thumbnail_img_url",
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

    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (POST 시 사용)",
    )

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
            "number_of_days",
            "status",
            "created_at",
            "updated_at",
            "thumbnail_img_file",
            "thumbnail_img_url",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    def create(self, validated_data: Dict[str, Any]) -> Subject:
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)
        instance = super().create(validated_data)

        if thumbnail_img_file:
            instance.thumbnail_img_url = f"http://actual-s3-bucket.com/media/{instance.id}/{thumbnail_img_file.name}"
            instance.save()

        return instance


class SubjectDetailSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 조회 API를 위한 시리얼라이저.
    GET 요청 시 특정 과목의 상세 정보를 정의합니다.
    """

    id = serializers.IntegerField(read_only=True)
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


class SubjectUpdateSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 수정 API를 위한 시리얼라이저.
    PATCH 요청 시 입력 및 응답 필드를 정의합니다.
    """

    id = serializers.IntegerField(read_only=True)
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    # PATCH 요청 시 파일을 받을 필드
    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (PATCH 시 사용)",
    )

    # 응답 시 URL을 반환할 필드
    thumbnail_img_url = serializers.URLField(
        read_only=True,
        help_text="썸네일 이미지 URL (응답 시 반환)",
    )

    class Meta:
        model = Subject
        fields = [
            "id",  # id 필드 명시적으로 포함
            "course_name",
            "title",
            "thumbnail_img_url",
            "thumbnail_img_file",
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    def update(self, instance: Subject, validated_data: Dict[str, Any]) -> Subject:
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)

        updated_instance = super().update(instance, validated_data)

        if thumbnail_img_file:
            updated_instance.thumbnail_img_url = (
                f"http://actual-s3-bucket.com/media/updated_{updated_instance.id}/{thumbnail_img_file.name}"
            )
            updated_instance.save()

        return updated_instance


# --- SubjectDropdownSerializer (프론트 요청 사항) ---
class SubjectDropdownSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 특정 과정의 과목 목록 조회 API (상태 필터링)를 위한 시리얼라이저.
    드롭다운 목록에 필요한 'id'와 'title' 필드만 포함합니다.
    """

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "title",
        ]
        read_only_fields = fields
