from rest_framework import serializers

from apps.courses.models import Course
from core.utils.s3_file_upload import S3Uploader


class CourseSerializer(serializers.ModelSerializer):
    thumbnail_img_file = serializers.ImageField(write_only=True, required=True)  # 리뷰 반영: required=True

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "thumbnail_img_file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "thumbnail_img_url"]

    def create(self, validated_data):
        thumbnail_file = validated_data.pop("thumbnail_img_file")
        key = f"courses/{thumbnail_file.name}"
        url = upload_file_to_s3(file=thumbnail_file, key=key)
        validated_data["thumbnail_img_url"] = url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        thumbnail_file = validated_data.pop("thumbnail_img_file", None)
        if thumbnail_file:
            key = f"courses/{thumbnail_file.name}"
            url = upload_file_to_s3(file=thumbnail_file, key=key)
            validated_data["thumbnail_img_url"] = url
        return super().update(instance, validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    generations_count = serializers.IntegerField(read_only=True)
    active_generations_count = serializers.IntegerField(read_only=True)
    total_students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "generations_count",
            "active_generations_count",
            "total_students_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
