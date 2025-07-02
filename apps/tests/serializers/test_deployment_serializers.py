from typing import Any, Dict

from rest_framework import serializers

from apps.tests.models import Test, TestDeployment


# 🔹 공통 timestamp serializer (선택적)
class BaseTimestampedSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        abstract = True
        fields = ["created_at", "updated_at"]


# 🔹 Test (쪽지시험)
class TestSerializer(BaseTimestampedSerializer):
    subject: Any = serializers.StringRelatedField()  # Subject 모델의 __str__() 출력


class Meta(BaseTimestampedSerializer.Meta):
    model = Test
    fields = ["id", "subject", "title", "thumbnail_img_url", *BaseTimestampedSerializer.Meta.fields]


# 활성화 ,비황성화
class DeploymentStatusUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = TestDeployment
        fields = ["status"]
        extra_kwargs = {"status": {"required": True}}


# 🔹 TestDeployment 생성
class DeploymentCreateSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(write_only=True, help_text="시험 ID")
    generation = serializers.IntegerField(help_text="기수 ID")

    class Meta:
        model = TestDeployment
        fields = [
            "test_id",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
        ]

    def create(self, validated_data: Dict[str, Any]) -> TestDeployment:
        # DB 조회나 MOCK 처리 없이, 단순히 create 호출
        return super().create(validated_data)


# 목록 조히 시리얼 라이저 ( 모델 기반으로 할려면 DB 필요)
class DeploymentListSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField(source="id")
    test_title = serializers.CharField(source="test.title")
    subject_title = serializers.CharField(source="test.subject.title")
    course_generation = serializers.SerializerMethodField()
    total_participants = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_course_generation(self, obj: Dict[str, Any]) -> str:
        course: str = obj.get("generation", {}).get("course", {}).get("title", "")
        generation: str = obj.get("generation", {}).get("name", "")
        return f"{course} {generation}"

    def get_total_participants(self, obj: Dict[str, Any]) -> int:
        return int(obj.get("total_participants", 0))

    def get_average_score(self, obj: Dict[str, Any]) -> float:
        return int(obj.get("average_score", 0.0))


class DeploymentDetailSerializer(serializers.Serializer[Any]):
    # 🔹 시험 정보
    test_id = serializers.IntegerField(source="test.id")
    test_title = serializers.CharField(source="test.title")
    subject_title = serializers.CharField(source="test.subject.title")
    question_count = serializers.SerializerMethodField()

    # 🔹 배포 정보
    deployment_id = serializers.IntegerField(source="id")
    access_code = serializers.CharField()
    access_url = serializers.SerializerMethodField()
    course_title = serializers.CharField(source="generation.course.title")
    generation_name = serializers.CharField(source="generation.name")
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    # 🔹 응시 정보
    total_participants = serializers.IntegerField()
    unsubmitted_participants = serializers.IntegerField()

    # ⬇️ Custom 필드 처리
    def get_access_url(self, obj: Any) -> str:
        return f"https://ozschool.com/test/{obj['id']}?code={obj['access_code']}"

    def get_question_count(self, obj: Any) -> int:
        snapshot = obj.get("questions_snapshot_json", {})
        return len(snapshot)


# # 🔹 참가코드 구현 (유효성 검사라서 모델을 계승하지 않음) (잘목 만듬)
# class AdminCodeValidationSerializer(serializers.Serializer[Any]):
#     deployment_id = serializers.IntegerField(help_text="배포 ID")
#     access_code = serializers.CharField(max_length=64, help_text="참가 코드")


class UserCodeValidationSerializer(serializers.Serializer[Any]):
    access_code = serializers.CharField(max_length=64, help_text="참가 코드만 입력")