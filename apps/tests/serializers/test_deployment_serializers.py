from typing import Any, Dict, List
from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.courses.models import Course, Generation
from apps.tests.core.utils.grading import (
    calculate_total_score,
    get_questions_snapshot_from_deployment,
    get_questions_snapshot_from_submission,
)
from apps.tests.models import Test, TestDeployment, TestQuestion, TestSubmission
from apps.tests.serializers.test_question_serializers import (
    UserTestQuestionStartSerializer,
)
from apps.tests.serializers.test_serializers import (
    AdminTestDetailSerializer,
    AdminTestListSerializer,
    UserTestSerializer,
)
from core.utils.base62 import generate_base62_code


# 공통 User&Admin
class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("id", "name")


# 관리자 쪽지 시험 응시 전체 목록 조회, 상세 조회
class AdminListCourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ("name",)


# 관리자 쪽지 시험 응시 전체 목록 조회, 상세 조회
class AdminListGenerationSerializer(serializers.ModelSerializer[Generation]):
    course = AdminListCourseSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = ("course", "number")


# 관리자 쪽지 시험 응시 상세 조회
class AdminTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestDetailSerializer(read_only=True)
    generation = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation",
            "duration_time",
            "open_at",
            "close_at",
            "question_count",
            "questions_snapshot_json",
        )


# 관리자 쪽지 시험 응시 전체 목록 조회
class AdminTestListDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = AdminTestListSerializer(read_only=True)
    generation = AdminListGenerationSerializer(read_only=True)

    class Meta:
        model = TestDeployment
        fields = (
            "test",
            "generation",
        )


# 사용자 쪽지 시험 응시: 요청, access_code 검증용
class UserTestStartSerializer(serializers.Serializer):
    access_code = serializers.CharField(write_only=True)

    # access_code 유효성 검사
    def validate_access_code(self, value: str) -> str:
        test_deployment = self.context["test_deployment"]

        if test_deployment.access_code != value:
            raise serializers.ValidationError("유효하지 않은 참가 코드입니다.")

        return value


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestDeploymentSerializer(serializers.ModelSerializer[TestDeployment]):
    test = UserTestSerializer(read_only=True)
    questions_snapshot_json = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment
        fields = (
            "id",
            "test",
            "duration_time",
            "questions_snapshot_json",
        )

    def get_questions_snapshot_json(self, obj):
        question_ids = [q["id"] for q in obj.questions_snapshot_json]
        questions = TestQuestion.objects.filter(id__in=question_ids)

        id_to_question = {q.id: q for q in questions}
        ordered_questions = [id_to_question[qid] for qid in question_ids if qid in id_to_question]

        return UserTestQuestionStartSerializer(ordered_questions, many=True).data


# 사용자 쪽지시험 목록조회
class UserTestDeploymentListSerializer(serializers.ModelSerializer[TestDeployment]):
    test = UserTestSerializer(read_only=True)

    question_score = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    correct_count = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment
        fields = ("id", "test", "question_count", "question_score", "submission_status", "score", "correct_count")

    def get_submission(self, obj: TestDeployment):
        student = self.context.get("student")
        if not student:
            return None
        return next((s for s in obj.submissions.all() if s.student_id == student.id), None)

    def get_question_score(self, obj: TestDeployment) -> int:
        snapshot = get_questions_snapshot_from_deployment(obj)
        return sum(question.get("point", 0) for question in snapshot)

    def get_submission_status(self, obj):
        student = self.context.get("student")
        if not student:
            return "확인 불가"
        has_submission = obj.submissions.filter(student=student).exists()  # prefetch_related 활용 가능
        return "응시 완료" if has_submission else "미응시"

    def get_score(self, obj):
        submission = self.get_submission(obj)
        return submission.score if submission else None

    def get_correct_count(self, obj):
        submission = self.get_submission(obj)
        return submission.correct_count if submission else None


# 사용자 쪽지 시험 목록 조회
class TestSubmissionListFilterSerializer(serializers.Serializer):
    course_title = serializers.CharField(required=False, allow_blank=True)
    generation_number = serializers.IntegerField(required=False)
    submission_status = serializers.ChoiceField(
        choices=[
            ("completed", "응시완료"),
            ("not_submitted", "미응시"),
        ],
        required=False,
    )


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


# 스냅샷 저장 로직( 배포 생성에 필요함)
def _generate_questions_snapshot_data(test_instance: Test) -> List[Dict[str, Any]]:
    if hasattr(test_instance, "questions") and test_instance.questions.exists():
        questions_data = [
            {
                "id": q.id,
                "question": q.question,
                "prompt": q.prompt,
                "type": q.type,
                "options_json": q.options_json,
                "answer": q.answer,
            }
            for q in test_instance.questions.all()
        ]
        return questions_data
    return []


# 활성화 ,비황성화
class DeploymentStatusUpdateSerializer(serializers.ModelSerializer):
    # CharField에 choices 옵션을 사용하여 유효성 검사 수행
    status = serializers.ChoiceField(choices=TestDeployment.TestStatus.choices, required=True)

    class Meta:
        model = TestDeployment
        fields = ["status"]


# 쪽지시험 배포 목록 조회
class DeploymentListSerializer(serializers.ModelSerializer[Any]):
    deployment_id = serializers.IntegerField(source="id", read_only=True)
    test_title = serializers.CharField(source="test.title", read_only=True)  #
    subject_title = serializers.CharField(source="test.subject.title", read_only=True)  #
    course_generation = serializers.SerializerMethodField()
    total_participants = serializers.IntegerField(read_only=True)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment  #
        fields = [
            "deployment_id",  #
            "test_title",
            "subject_title",
            "course_generation",
            "total_participants",
            "average_score",
            "status",  #
            "created_at",  #
        ]

    def get_course_generation(self, obj: Any) -> str:
        course_name = obj.generation.course.name if obj.generation and obj.generation.course else ""
        generation_number = obj.generation.number if obj.generation else ""
        return f"{course_name} {generation_number}기"

    def get_average_score(self, obj: TestDeployment) -> float:

        # 각 배포의 제출된 시험들의 평균 점수를 계산합니다.
        submissions = obj.submissions.all()  # 해당 배포의 모든 제출을 가져옵니다.

        if not submissions:
            return 0.0  # 제출이 없으면 평균 점수는 0입니다.

        total_scores_sum = 0.0

        # 각 제출을 반복하며 점수를 계산하고 합산합니다.
        for submission in submissions:
            snapshot = get_questions_snapshot_from_submission(submission)
            submission_score = calculate_total_score(submission.answers_json, snapshot)
            total_scores_sum += submission_score

        # 전체 제출의 총합 점수를 제출 수로 나누어 평균을 계산합니다.
        return total_scores_sum / len(submissions)


# 쪽지 시험 배포 상세 조회
class DeploymentDetailSerializer(serializers.ModelSerializer):
    # 시험 정보
    test_id = serializers.IntegerField(source="test.id", read_only=True)
    test_title = serializers.CharField(source="test.title", read_only=True)
    subject_title = serializers.CharField(source="test.subject.title", read_only=True)
    question_count = serializers.SerializerMethodField()  # 시험 문항 수 (계산 필요)

    # 배포 정보
    access_url = serializers.SerializerMethodField()  # 시험 응시 링크 URL (계산 필요)
    course_title = serializers.CharField(source="generation.course.name", read_only=True)  # 과정 이름
    generation_name = serializers.CharField(source="generation.name", read_only=True)  # 기수 이름

    # 응시 정보
    total_participants = serializers.IntegerField(read_only=True)
    total_generation_students = serializers.IntegerField(read_only=True)
    unsubmitted_participants = serializers.SerializerMethodField()  # 미참여 인원수 (계산 필요)

    # 평균 점수 추가 (상세 조회에서도 필요하다면)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment
        fields = [
            # 시험 정보
            "test_id",
            "test_title",
            "subject_title",
            "question_count",
            # 배포 정보
            "id",  # 배포 고유 ID
            "access_code",
            "access_url",
            "course_title",
            "generation_name",
            "duration_time",
            "open_at",
            "close_at",
            "status",
            "created_at",
            "updated_at",  # 배포 수정 일시
            # 응시 정보
            "total_participants",
            "total_generation_students",
            "unsubmitted_participants",
            "average_score",
        ]
        read_only_fields = fields  # 모든 필드를 읽기 전용으로 설정

    # Custom 필드 처리 메서드️
    def get_question_count(self, obj: TestDeployment) -> int:
        # TestDeployment의 questions_snapshot_json을 사용하여 시험 문항 수를 반환합니다.
        snapshot = obj.questions_snapshot_json
        if isinstance(snapshot, dict) and "questions" in snapshot:
            return len(snapshot["questions"])
        elif isinstance(snapshot, list):
            return len(snapshot)
        return 0

    def get_unsubmitted_participants(self, obj: TestDeployment) -> int:
        # 미참여 인원 수를 계산하여 반환합니다.
        total_participants = getattr(obj, "total_participants", 0)
        total_generation_students = getattr(obj, "total_generation_students", 0)
        return max(0, total_generation_students - total_participants)

    def get_average_score(self, obj: TestDeployment) -> float:

        # 이 배포의 제출된 시험들의 평균 점수를 계산합니다.
        submissions = obj.submissions.all()

        if not submissions:
            return 0.0

        total_scores_sum = 0.0
        questions_snapshot = obj.questions_snapshot_json  # 배포의 스냅샷을 사용

        for submission in submissions:
            # grading.py의 calculate_total_score 함수를 직접 호출하여 점수 계산
            submission_score = calculate_total_score(submission.answers_json, questions_snapshot)  #
            total_scores_sum += submission_score

        return total_scores_sum / len(submissions)

    def get_access_url(self, obj):
        request = self.context["request"]

        # Referer → Origin 순으로 도메인 확보
        client_host = None
        referer = request.META.get("HTTP_REFERER")
        origin = request.META.get("HTTP_ORIGIN")

        if referer:
            parsed = urlparse(referer)
            client_host = f"{parsed.scheme}://{parsed.netloc}"
        elif origin:
            parsed = urlparse(origin)
            client_host = f"{parsed.scheme}://{parsed.netloc}"

        # referer, origin 이 둘다 존재하지 않으면 도메인 리턴
        if not client_host:
            client_host = "https://tomato-test.kro.kr"

        return f"{client_host}/exam/{obj.id}"


# 쪽지시험 배포 생성
class DeploymentCreateSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(write_only=True, help_text="시험 ID")
    generation_id = serializers.IntegerField(write_only=True, help_text="기수 ID")

    class Meta:
        model = TestDeployment
        fields = [
            "test_id",
            "generation_id",
            "duration_time",
            "open_at",
            "close_at",
            "status",
        ]
        read_only_fields = ["access_code", "status", "questions_snapshot_json"]

    def create(self, validated_data):
        test_id = validated_data.pop("test_id")
        generation_id = validated_data.pop("generation_id")

        # 시험 ID로 Test 모델 객체를 조회하고 없으면 유효하지 않은 시험 ID라고 에러메시지 발생
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise ValidationError({"test_id": "유효하지 않은 시험 ID 입니다."})

        # 기수 ID Generation 모델 객체를 조회하고, 없으면 유효하지 않은 기수 ID 입니다 에러메시지 발생
        try:
            # 변수명 충돌을 피하기 위해 'generation.obj로 변경
            generation_obj = Generation.objects.get(id=generation_id)
        except Generation.DoesNotExist:
            raise ValidationError({"generation_id": "유효하지 않은 기수 ID 입니다."})

        # Base62 인코딩 함수를 호출하며 6자리 길이 지정을 요청
        generated_code = generate_base62_code()

        validated_data["access_code"] = generated_code
        validated_data["status"] = "Activated"

        # _generate_questions_snapshot_data 함수를 호출하여 questions_snapshot_json 필드 채우기
        questions_snapshot_data = _generate_questions_snapshot_data(test)
        validated_data["questions_snapshot_json"] = questions_snapshot_data

        return TestDeployment.objects.create(
            test=test,
            generation=generation_obj,
            **validated_data,
        )


# 참가 코드 검증 (user)
class UserCodeValidationSerializer(serializers.Serializer):
    access_code = serializers.CharField(write_only=True)

    def validate_access_code(self, value: str) -> str:
        test_deployment = self.context["test_deployment"]
        if test_deployment.access_code != value:
            raise serializers.ValidationError("유효하지 않은 참가코드입니다.")
        return value
