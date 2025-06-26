# 쪽지 시험 응시
from rest_framework import serializers

from apps.tests.models import Test, TestDeployment


class TestSerializer(serializers.ModelSerializer[Test]):
    class Meta:
        model = Test
        fields = [
            "id",
            "title",
            "thumbnail_img_url",
        ]


class TestStartSerializer(serializers.ModelSerializer[TestDeployment]):
    test = TestSerializer(read_only=True)
    access_code = serializers.CharField(write_only=True)

    class Meta:
        model = TestDeployment
        fields = [
            "id",
            "test",
            "generation",
            "test",
            "duration_time",
            "test_id",
            "access_code",
            "open_at",
            "close_at",
            "questions_snapshot_json",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "test",
            "generation",
            "test",
            "duration_time",
            "open_at",
            "close_at",
            "questions_snapshot_json",
            "status",
            "created_at",
            "updated_at",
        ]
