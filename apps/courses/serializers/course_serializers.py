from rest_framework import serializers

from apps.courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    thumbnail_img_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "thumbnail_img_file",  # 추가됨
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "thumbnail_img_url"]

    def create(self, validated_data):
        thumbnail_file = validated_data.pop("thumbnail_img_file", None)

        # 실제 파일 저장 처리 (예: 로컬 또는 S3)
        # 여기선 단순히 로컬 경로 가정
        if thumbnail_file:
            filename = f"courses/{thumbnail_file.name}"
            with open(f"media/{filename}", "wb") as f:
                for chunk in thumbnail_file.chunks():
                    f.write(chunk)
            validated_data["thumbnail_img_url"] = f"/media/{filename}"

        return super().create(validated_data)


# 과정 목록 조회용 시리얼라이저 (집계 필드 포함)
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
