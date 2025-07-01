from typing import Any, Dict  # Dict 임포트 유지

from rest_framework import serializers

# 실제 모델 임포트
from apps.courses.models import Course, Subject


# --- SubjectListSerializer (목록 조회용) ---
class SubjectListSerializer(serializers.ModelSerializer[Subject]):
    # id 필드를 BIGINT 또는 integer로 명시 (API 명세의 응답 필드 타입: integer)
    # Django 기본 id는 int이므로, BigIntegerField가 아니라면 integer가 적합합니다.
    id = serializers.IntegerField(read_only=True)  # <--- id 필드 타입 명시 (API 명세 반영)
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름")

    class Meta:
        model = Subject
        fields = [
            "id",  # id 필드 명시적으로 포함
            "title",
            "number_of_days",
            "number_of_hours",
            "course_name",
            "status",
            "created_at",
            "updated_at",
            "thumbnail_img_url",  # 목록 조회에도 포함
        ]
        read_only_fields = fields  # 모든 필드를 read_only로 설정하여 GET 요청 전용임을 명확히 함


# --- SubjectSerializer (과목 등록용 - POST 요청) ---
class SubjectSerializer(serializers.ModelSerializer[Subject]):
    """
    과목 등록 (POST) API를 위한 시리얼라이저.
    입력 필드와 생성 후 반환될 필드를 정의합니다.
    """

    # PrimaryKeyRelatedField를 다시 사용하여 실제 Course 모델 참조
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),  # 실제 Course 객체를 조회
        source="course",  # 모델의 'course' 필드와 매핑
        write_only=True,
        help_text="이 과목이 속할 과정의 고유 ID (입력 전용)",
    )

    course_name = serializers.CharField(source="course.name", read_only=True, help_text="과목이 속한 과정의 이름")

    # POST 요청 시 파일을 받을 필드
    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (POST 시 사용)",
    )

    # 응답 시 URL을 반환할 필드
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
            "thumbnail_img_file",  # 파일 입력을 위한 필드
            "thumbnail_img_url",  # URL 출력을 위한 필드 (read_only)
        ]
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    def create(self, validated_data: Dict[str, Any]) -> Subject:
        # thumbnail_img_file은 FileField이므로 validated_data에서 실제 파일 객체로 넘어옴
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)

        # 실제 Subject 모델 인스턴스 생성
        # validated_data에는 'course' 인스턴스가 포함되어 있음 (PrimaryKeyRelatedField의 source='course' 덕분)
        instance = super().create(validated_data)  # super().create는 Course 인스턴스를 받아서 ForeignKey 연결

        if thumbnail_img_file:
            # 실제 파일 저장 로직 (예: AWS S3에 업로드 후 URL 반환)
            # 이 부분은 실제 서비스 환경에 맞춰 구현해야 합니다.
            # 예시: s3_file_path = upload_to_s3(thumbnail_img_file, instance.id)
            # instance.thumbnail_img_url = f"https://your-s3-bucket.s3.amazonaws.com/{s3_file_path}"

            # 현재는 Mock URL을 사용합니다.
            instance.thumbnail_img_url = f"http://actual-s3-bucket.com/media/{instance.id}/{thumbnail_img_file.name}"
            instance.save()  # URL 업데이트 저장

        return instance


# --- SubjectDetailSerializer (상세 조회용 - GET 요청) ---
class SubjectDetailSerializer(serializers.ModelSerializer[Subject]):
    """
    (Admin) 등록된 수강 과목 상세 조회 API를 위한 시리얼라이저.
    GET 요청 시 특정 과목의 상세 정보를 정의합니다.
    """

    # id 필드를 BIGINT 또는 integer로 명시 (API 명세의 응답 필드 타입: integer)
    id = serializers.IntegerField(read_only=True)  # <--- id 필드 타입 명시 (API 명세 반영)
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",  # id 필드 명시적으로 포함
            "title",
            "thumbnail_img_url",  # URL 필드는 여기에 그대로 유지
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

    # id 필드를 BIGINT 또는 integer로 명시 (API 명세의 응답 필드 타입: integer)
    id = serializers.IntegerField(read_only=True)  # <--- id 필드 타입 명시 (API 명세 반영)
    course_name = serializers.CharField(source="course.name", help_text="과목이 속한 과정의 이름", read_only=True)

    # PATCH 요청 시 파일을 받을 필드
    thumbnail_img_file = serializers.FileField(
        write_only=True,
        required=False,
        help_text="업로드할 썸네일 이미지 파일 (PATCH 시 사용)",
    )

    # 응답 시 URL을 반환할 필드
    thumbnail_img_url = serializers.URLField(
        read_only=True,  # PATCH 응답에서도 URL을 보여주지만, 이 필드 자체는 입력으로 받지 않음
        help_text="썸네일 이미지 URL (응답 시 반환)",
    )

    class Meta:
        model = Subject
        fields = [
            "id",  # id 필드 명시적으로 포함
            "course_name",
            "title",
            "thumbnail_img_url",
            "thumbnail_img_file",  # 파일 입력을 위한 필드 (PATCH 시 사용)
            "number_of_days",
            "number_of_hours",
            "status",
            "created_at",
            "updated_at",
        ]
        # read_only_fields에서 thumbnail_img_url을 다시 read_only로 설정하여,
        # API 명세와 같이 PATCH 요청 본문에 URL을 직접 받는 것이 아니라,
        # 파일이 업로드되면 자동으로 URL이 생성되어 반환되는 것을 반영.
        read_only_fields = ["id", "created_at", "updated_at", "course_name", "thumbnail_img_url"]

    def update(self, instance: Subject, validated_data: Dict[str, Any]) -> Subject:
        # thumbnail_img_file이 전달되면 처리
        thumbnail_img_file = validated_data.pop("thumbnail_img_file", None)

        # 모델 인스턴스 업데이트
        updated_instance = super().update(instance, validated_data)

        if thumbnail_img_file:
            # 실제 파일 저장 로직 (예: AWS S3에 업로드 후 URL 반환)
            # 기존 파일 삭제 로직 추가 (선택 사항, 필요 시 구현)
            # 예시: s3_url = upload_to_s3(thumbnail_img_file, updated_instance.id)
            # updated_instance.thumbnail_img_url = f"https://your-s3-bucket.s3.amazonaws.com/{s3_url}"

            # 현재는 Mock URL을 사용합니다.
            updated_instance.thumbnail_img_url = (
                f"http://actual-s3-bucket.com/media/updated_{updated_instance.id}/{thumbnail_img_file.name}"
            )
            updated_instance.save()  # URL 업데이트 저장

        return updated_instance
