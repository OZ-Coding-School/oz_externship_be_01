from rest_framework import serializers
# 참가코드 구현
class CodeValidationRequestSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()
    access_code = serializers.CharField(max_length=64)

# 쪽지시험 배포 생성
class DeploymentCreateSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    generation_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()


# 배포 목록 조회용
class DeploymentListSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()
    test_title = serializers.CharField()
    subject_title = serializers.CharField()
    course_generation = serializers.CharField()
    total_participants = serializers.IntegerField()
    average_score = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
# 배포 상세 조회용
class TestSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()
    test_title = serializers.CharField()
    subject_title = serializers.CharField()
    question_count = serializers.IntegerField()


class DeploymentSerializer(serializers.Serializer):
    deployment_id = serializers.IntegerField()
    access_url = serializers.URLField()
    access_code = serializers.CharField()
    course_title = serializers.CharField()  # 모델 필드명 반영
    generation_title = serializers.CharField()
    duration_time = serializers.IntegerField()  # 모델 필드명 반영
    open_at = serializers.DateTimeField()       # 모델 필드명 반영
    close_at = serializers.DateTimeField()      # 모델 필드명 반영
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()



class SubmissionStatsSerializer(serializers.Serializer):
    total_participants = serializers.IntegerField()
    not_participated = serializers.IntegerField()   # 필드명 통일


class DeploymentDetailSerializer(serializers.Serializer):
    test = TestSerializer()
    deployment = DeploymentSerializer()
    submission_stats = SubmissionStatsSerializer()
