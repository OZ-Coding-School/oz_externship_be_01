from typing import Any
from rest_framework import serializers
from rest_framework.serializers import Serializer


class CodeValidationRequestSerializer(Serializer[Any]):
    deployment_id = serializers.IntegerField()
    access_code = serializers.CharField(max_length=64)


class DeploymentCreateSerializer(Serializer[Any]):
    test_id = serializers.IntegerField()
    generation_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()


class DeploymentListSerializer(Serializer[Any]):
    deployment_id = serializers.IntegerField()
    test_title = serializers.CharField()
    subject_title = serializers.CharField()
    course_generation = serializers.CharField()
    total_participants = serializers.IntegerField()
    average_score = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class TestSerializer(Serializer[Any]):
    test_id = serializers.IntegerField()
    test_title = serializers.CharField()
    subject_title = serializers.CharField()
    question_count = serializers.IntegerField()


class DeploymentSerializer(Serializer[Any]):
    deployment_id = serializers.IntegerField()
    access_url = serializers.URLField()
    access_code = serializers.CharField()
    course_title = serializers.CharField()
    generation_title = serializers.CharField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class SubmissionStatsSerializer(Serializer[Any]):
    total_participants = serializers.IntegerField()
    not_participated = serializers.IntegerField()


class DeploymentDetailSerializer(Serializer[Any]):
    test = TestSerializer()
    deployment = DeploymentSerializer()
    submission_stats = SubmissionStatsSerializer()
