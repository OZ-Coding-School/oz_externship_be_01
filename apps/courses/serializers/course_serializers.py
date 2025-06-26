from rest_framework import serializers

from apps.courses.models import Course


# --- CourseListSerializer (목록 조회용) ---
class CourseListSerializer(serializers.ModelSerializer[Course]):

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# --- CourseSerializer (등록/수정/상세 조회용) ---
class CourseSerializer(serializers.ModelSerializer[Course]):

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
