import json
from typing import Any, Dict, List

from rest_framework import serializers

# 명시적으로 임포트하여 사용합니다.
from rest_framework.exceptions import ValidationError

from apps.courses.models import Course, Generation
from apps.tests.core.utils.grading import calculate_total_score
from apps.tests.models import Test, TestDeployment, TestQuestion
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


# 삭제 공유
# 공통 User&Admin
# class GenerationSerializer(serializers.ModelSerializer[Generation]):
#     course = CourseSerializer(read_only=True)
#
#     class Meta:
#         model = Generation
#         fields = ("id", "course", "number")


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
class DeploymentStatusUpdateSerializer(serializers.ModelSerializer[Any]):
    class Meta:
        model = TestDeployment
        fields = ["status"]
        extra_kwargs = {"status": {"required": True}}


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
            submission_score = calculate_total_score(submission.answers_json)
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
    unsubmitted_participants = serializers.SerializerMethodField()  # 미참여 인원수 (계산 필요)

    # 평균 점수 추가 (상세 조회에서도 필요하다면)
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = TestDeployment  # ModelSerializer이므로 모델 지정
        fields = [
            # 시험 정보
            "test_id",
            "test_title",
            "subject_title",
            "question_count",  # Meta.fields에 question_count를 사용합니다.
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
            "unsubmitted_participants",
            "average_score",
        ]
        read_only_fields = fields  # 모든 필드를 읽기 전용으로 설정

    # Custom 필드 처리 메서드️

    def get_question_count(self, obj: TestDeployment) -> int:
        """TestDeployment의 questions_snapshot_json을 사용하여 시험 문항 수를 반환합니다."""
        snapshot = obj.questions_snapshot_json
        if isinstance(snapshot, dict) and "questions" in snapshot:
            return len(snapshot["questions"])
        elif isinstance(snapshot, list):
            return len(snapshot)
        return 0

        # 시험 응시 링크 URL을 반환합니다.

    def get_access_url(self, obj: TestDeployment) -> str:
        # 실제 서비스 URL은 Django settings에서 가져오는 것이 좋습니다.
        return f"https://ozschool.com/test/{obj.id}?code={obj.access_code}"

    def get_unsubmitted_participants(self, obj: TestDeployment) -> int:
        # 미참여 인원 수를 계산하여 반환합니다.
        total_participants = getattr(obj, "total_participants", 0)
        # 뷰에서 annotate된 total_generation_students 값을 사용합니다.
        # 뷰의 쿼리셋에 `total_generation_students=Count('generation__students', distinct=True)`가 필요합니다.
        total_generation_students = getattr(obj, "total_generation_students", 0)
        return max(0, total_generation_students - total_participants)

    def get_average_score(self, obj: TestDeployment) -> float:

        # 이 배포의 제출된 시험들의 평균 점수를 계산합니다.
        submissions = obj.submissions.all()

        if not submissions:
            return 0.0

        total_scores_sum = 0.0
        questions_snapshot = obj.questions_snapshot_json

        for submission in submissions:
            # 시리얼라이저 내부의 헬퍼 메서드를 호출
            submission_score = self._calculate_score_for_single_submission(submission.answers_json, questions_snapshot)
            total_scores_sum += submission_score

        return total_scores_sum / len(submissions)

    # _calculate_score_for_single_submission 헬퍼 메서드
    def _calculate_score_for_single_submission(
        self, submitted_answers: Dict[str, Any], questions_snapshot: List[Dict[str, Any]]
    ) -> float:
        """
        단일 제출에 대한 점수를 계산합니다.
        문제 유형별 채점 로직을 내부 헬퍼 함수와 딕셔너리를 사용하여 최적화합니다.
        """

        # 문제 유형별 채점 헬퍼 함수들 (메서드 내부에 정의)
        def _score_multiple_choice(correct_ans: Any, submitted_ans: Any, point: int) -> float:
            correct_options = correct_ans
            if isinstance(correct_ans, str):
                try:
                    correct_options = json.loads(correct_ans)
                except json.JSONDecodeError:
                    return 0.0

            submitted_options = submitted_ans
            if isinstance(submitted_ans, str):
                try:
                    submitted_options = json.loads(submitted_ans)
                except json.JSONDecodeError:
                    return 0.0

            if isinstance(correct_options, list) and isinstance(submitted_options, list):
                if set(correct_options) == set(submitted_options):
                    return float(point)
            elif correct_options == submitted_options:
                return float(point)
            return 0.0

        def _score_short_answer(correct_ans: Any, submitted_ans: Any, point: int) -> float:
            if str(correct_ans).strip().lower() == str(submitted_ans).strip().lower():
                return float(point)
            return 0.0

        def _score_ordering(correct_ans: Any, submitted_ans: Any, point: int) -> float:
            correct_order = correct_ans
            if isinstance(correct_ans, str):
                try:
                    correct_order = json.loads(correct_ans)
                except json.JSONDecodeError:
                    return 0.0

            submitted_order = submitted_ans
            if isinstance(submitted_ans, str):
                try:
                    submitted_order = json.loads(submitted_ans)
                except json.JSONDecodeError:
                    return 0.0

            if (
                isinstance(correct_order, list)
                and isinstance(submitted_order, list)
                and correct_order == submitted_order
            ):
                return float(point)
            return 0.0

        def _score_fill_in_blank(correct_ans: Any, submitted_ans: Any, point: int) -> float:
            correct_blanks = correct_ans
            if isinstance(correct_ans, str):
                try:
                    correct_blanks = json.loads(correct_ans)
                except json.JSONDecodeError:
                    return 0.0

            submitted_blanks = submitted_ans
            if isinstance(submitted_ans, str):
                try:
                    submitted_blanks = json.loads(submitted_ans)
                except json.JSONDecodeError:
                    return 0.0

            if isinstance(correct_blanks, dict) and isinstance(submitted_blanks, dict):
                is_correct_all_blanks = True
                for key, val in correct_blanks.items():
                    if str(submitted_blanks.get(key, "")).strip().lower() != str(val).strip().lower():
                        is_correct_all_blanks = False
                        break
                if is_correct_all_blanks:
                    return float(point)
            return 0.0

        # 문제 유형별 채점 함수 매핑
        scoring_functions = {
            TestQuestion.QuestionType.MULTIPLE_CHOICE_SINGLE.value: _score_multiple_choice,  # type: ignore
            TestQuestion.QuestionType.MULTIPLE_CHOICE_MULTI.value: _score_multiple_choice,  # type: ignore
            TestQuestion.QuestionType.OX.value: _score_multiple_choice,  # type: ignore
            TestQuestion.QuestionType.SHORT_ANSWER.value: _score_short_answer,  # type: ignore
            TestQuestion.QuestionType.ORDERING.value: _score_ordering,  # type: ignore
            TestQuestion.QuestionType.FILL_IN_BLANK.value: _score_fill_in_blank,  # type: ignore
        }

        total_score_for_submission = 0.0
        for q_snapshot in questions_snapshot:
            question_id = str(q_snapshot.get("id"))
            correct_answer = q_snapshot.get("answer")
            question_point = q_snapshot.get("point", 0)
            question_type = q_snapshot.get("type")

            submitted_answer = submitted_answers.get(question_id)

            # 정답과 제출된 답안이 모두 존재하고, 채점 함수가 정의된 경우에만 채점
            if correct_answer is not None and submitted_answer is not None and question_type in scoring_functions:
                score_func = scoring_functions[question_type]
                total_score_for_submission += score_func(correct_answer, submitted_answer, question_point)

        return total_score_for_submission


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
