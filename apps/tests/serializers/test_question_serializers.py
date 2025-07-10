from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.exceptions import NotFound

from apps.tests.models import Test, TestQuestion


# 등록
class TestQuestionCreateSerializer(serializers.ModelSerializer):  # type: ignore
    test_id = serializers.IntegerField(write_only=True)
    test: PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(read_only=True)
    prompt = serializers.CharField(required=False, allow_blank=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
    answer = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TestQuestion
        fields = "__all__"

    def validate(self, data):
        from apps.tests.models import Test

        test_id = data.get("test_id")
        if not test_id:
            raise serializers.ValidationError("test_id는 필수입니다.")
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise NotFound("해당 ID의 쪽지시험이 존재하지 않습니다.")

        # 문제 개수 제한 (최대 20개)
        if test.questions.count() > 20:
            raise serializers.ValidationError("쪽지시험 당 최대 20문제까지만 등록할 수 있습니다.")

        # 배점 합산 제한 (쵀대 100점)
        current_total = sum(q.point for q in test.questions.all())
        if current_total + data.get("point", 0) > 100:
            raise serializers.ValidationError(" 총 배점은 100점을 초과할 수 없습니다.")

        q_type = data.get("type")
        if not q_type:
            raise serializers.ValidationError("문제 유형(type)은 필수입니다.")

        # 빈칸 채우기 문제
        if q_type == "fill_in_blank":
            if not data.get("prompt"):
                raise serializers.ValidationError("빈칸 채우기 문제는 prompt(지문)이 필요합니다.")
            if not data.get("blank_count") or data["blank_count"] < 1:
                raise serializers.ValidationError("빈칸 개수는 1개 이상이어야 합니다.")
            if not data.get("answer"):
                raise serializers.ValidationError("빈칸 채우기 문제는 answer(정답)이 필요합니다.")
            data["options_json"] = None

        # 다지선다형 문제
        elif q_type == "multiple_choice_single":  # 단일
            options = data.get("options_json")
            answer = data.get("answer")

            if not isinstance(options, list) or len(options) < 2:
                raise serializers.ValidationError("객관식은 options_json(보기)가 2개 이상 필요합니다.")
            if not isinstance(answer, list) or len(answer) != 1:
                raise serializers.ValidationError("단일 선택 객관식은 정답(answer)을 하나만 리스트로 입력해야 합니다.")

            if answer[0] not in options:
                raise serializers.ValidationError(f"정답 '{answer[0]}'이 보기 목록에 없습니다.")

        elif q_type == "multiple_choice_multi":  # 다중
            options = data.get("options_json")
            answer = data.get("answer")

            if not isinstance(options, list) or len(options) < 2:  # 다지 선다형이라 정답 2개 이상 적어야 통과
                raise serializers.ValidationError("객관식은 options_json(보기)가 2개 이상 필요합니다.")
            if not isinstance(answer, list) or len(answer) < 2:
                raise serializers.ValidationError(
                    "다중 선택 객관식은 두개 이상의 정답(answer)을 리스트로 입력해야 합니다."
                )

            invalid_answers = [a for a in answer if a not in options]  # 문제에 없는 정답 적으면 오류 출력
            if invalid_answers:
                raise serializers.ValidationError(f"다음 정답은 보기 목록에 없습니다: {invalid_answers}")

        # 주관식 단답형 문제
        elif q_type == "short_answer":
            if not data.get("answer"):
                raise serializers.ValidationError("주관식 단답형 answer(정답)이 필요합니다.")
            if not isinstance(data.get("answer"), list) or not data["answer"]:
                raise serializers.ValidationError("정답(answer)은 리스트 형태로 입력해야 합니다.")
            data["options_json"] = None
            data["prompt"] = None
            data["blank_count"] = None

        # 순서 정렬 문제
        elif q_type == "ordering":
            options = data.get("options_json", [])
            answer = data.get("answer", [])

            if not isinstance(options, list) or len(options) < 2:
                raise serializers.ValidationError("순서 정렬형 문제는 최소 2개의 보기가 필요합니다.")
            if not isinstance(answer, list) or len(answer) != len(options):
                raise serializers.ValidationError("정답(answer)은 보기(options_json)와 동일한 개수여야 합니다.")

            if sorted(answer) != sorted(options):
                raise serializers.ValidationError(
                    "정답(answer)은 보기(options_json) 안에 있는 문제와 동일 해야합니다. "
                )

            data["prompt"] = None
            data["blank_count"] = None

        # OX 문제
        elif q_type == "ox":
            answer_list = data.get("answer")
            # answer는 반드시 리스트 형태로 하나의 값만 포함해야 함
            if not isinstance(answer_list, str):
                raise serializers.ValidationError('OX 퀴즈는 정답을 하나만 리스트로 입력해야 합니다.')
            # 정답 값 검증
            answer_value = answer_list[0]
            if answer_value not in ["O", "X", "o", "x"]:
                raise serializers.ValidationError("OX 퀴즈 정답은 'O' 또는 'X' 형식이어야 합니다.")
            # 필요 없는 필드 초기화
            data["options_json"] = None
            data["prompt"] = None
            data["blank_count"] = None
        else:
            raise serializers.ValidationError(f"지원하지 않는 문제 유형입니다: {q_type}")

        return data

    def create(self, validated_data):
        from apps.tests.models import Test

        test_id = validated_data.pop("test_id")
        test = Test.objects.get(id=test_id)
        return TestQuestion.objects.create(test=test, **validated_data)


# 수정
class TestQuestionUpdateSerializer(serializers.ModelSerializer):  # type: ignore
    prompt = serializers.CharField(required=False, allow_blank=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
    answer = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TestQuestion
        fields = [
            "type",
            "question",
            "prompt",
            "blank_count",
            "options_json",
            "answer",
            "point",
            "explanation",
        ]

    # 요청값 기준으로만 판단
    def validate(self, data):
        question_type = data.get("type", None)
        answer = data.get("answer", None)
        point = data.get("point", None)
        options = data.get("options_json", None)
        prompt = data.get("prompt", None)
        blank_count = data.get("blank_count", None)

        if not question_type:
            raise serializers.ValidationError({"detail": "문제 유형(type)은 필수입니다."})

        if point is not None and not (1 <= point <= 10):
            raise serializers.ValidationError({"detail": "배점은 1~10점 사이여야 합니다."})

        # 유형별 필드 검증 및 불필요한 필드 초기화
        if question_type == "multiple choice":
            if not options:
                raise serializers.ValidationError({"detail": "다지선다형은 'option_json'이 필수입니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다."})

            data["prompt"] = None
            data["options_json"] = None

        elif question_type == "blank_count":
            if not prompt:
                raise serializers.ValidationError({"detail": "빈칸 문제는 'prompt'가 필요합니다."})
            if blank_count is None or blank_count < 1:
                raise serializers.ValidationError({"detail": "blank_count는 1이상이어야 합니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다."})

            data["options_json"] = None

        elif question_type == "subjective":
            if not answer:
                raise serializers.ValidationError({"detail": "주관식 문제는 정답이 필요합니다."})

            data["prompt"] = None
            data["options_json"] = None
            data["blank_count"] = None

        elif question_type == "order":
            if not options or len(options) < 2:
                raise serializers.ValidationError({"detail": "순서 문제는 보기(options_json) 2개 이상 필요합니다."})
            if not answer:
                raise serializers.ValidationError({"detail": "정답이 필요합니다.."})

            data["prompt"] = None
            data["blank_count"] = None

        elif question_type == "ox":
            if answer not in [["o"], ["x"]]:
                raise serializers.ValidationError({"detail": "ox 문제는 정답이 ['o'] 또는 ['x']여야 합니다."})

            data["prompt"] = None
            data["blank_count"] = None
            data["options_json"] = None

        else:
            raise serializers.ValidationError({"detail": f"지원하지 않는 문제 유형입니다: {question_type}"})

        return data


# 목록 조회
class TestListItemSerializer(serializers.ModelSerializer):  # type: ignore
    test_id = serializers.IntegerField(source="id")
    test_title = serializers.CharField(source="title")
    subject_title = serializers.CharField(source="subject.title")
    question_count = serializers.IntegerField()
    total_score = serializers.IntegerField()

    submission_status = serializers.ChoiceField(choices=["submitted", "not_submitted"])
    score = serializers.IntegerField(required=False, allow_null=True)
    correct_count = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Test
        fields = [
            "test_id",
            "test_title",
            "thumbnail_img_url",
            "subject_title",
            "question_count",
            "total_score",
            "submission_status",
            "score",
            "correct_count",
        ]


# 삭제 응답
class ErrorResponseSerializer(serializers.Serializer):  # type: ignore
    detail = serializers.CharField()


# 사용자 쪽지 시험 응시: 응답, 시험 정보 응답용
class UserTestQuestionStartSerializer(serializers.ModelSerializer[TestQuestion]):
    class Meta:
        model = TestQuestion
        fields = ("type", "question", "prompt", "blank_count", "options_json", "point")
