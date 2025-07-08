from rest_framework import serializers

from apps.tests.models import Test, TestQuestion


# 등록
class TestQuestionCreateSerializer(serializers.ModelSerializer):  # type: ignore
    test_id = serializers.IntegerField(write_only=True)
    prompt = serializers.CharField(required=False, allow_blank=True)
    blank_count = serializers.IntegerField(required=False, allow_null=True)
    options_json = serializers.ListField(child=serializers.CharField(), required=False)
    answer = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TestQuestion
        fields = "__all__"

    def validate(self, data):
        test = data.get("test")
        if not test:
            raise serializers.ValidationError("유효한 쪽지시험이 필요합니다.")

        # 문제 개수 제한 (최대 20개)
        if test.questions.count() >= 20:
            raise serializers.ValidationError("쪽지시험 당 최대 20문제까지만 등록할 수 있습니다.")

        # 배점 합산 제한 (쵀대 100점)
        current_total = sum(q.point for q in test.questions.all())
        if current_total + data.get("point", 0) > 100:
            raise serializers.ValidationError(" 총 배점은 100점을 초과할 수 없습니다.")

        # 문제 유형별 필드 체크
        q_type = data.get("type")

        if q_type == "multiple_choice_single" or q_type == "multiple_choice_multiple":
            if not data.get("options_json"):
                raise serializers.ValidationError("객관신은 options_json(보기)가 필요합니다.")
            if not data.get("answer"):
                raise serializers.ValidationError("객관식은 answer(정답)가 필요합니다.")

        elif q_type == "fill_in_blank":
            if not data.get("prompt"):
                raise serializers.ValidationError("빈칸 채우기 문제는 prompt(지문)이 필요합니다.")
            if not data.get("blank_count") or data.get("blank_count") < 1:
                raise serializers.ValidationError("빈칸 개수는 1개 이상이어야 합니다.")
            if not data.get("answer"):
                raise serializers.ValidationError("빈칸 채우기 문제는 answer(정답)이 필요합니다.")

        elif q_type == "short_answer":
            if not data.get("answer"):
                raise serializers.ValidationError("주관식 단답형 answer(정답)이 필요합니다.")


        elif q_type == "ordering":
            if not data.get("options_json") or len(eval(data.get("options_json", "[]"))) < 2:
                raise serializers.ValidationError("순서 정렬형 문제는 최소 2개의 보기가 필요합니다.")

            if not data.get("answer"):
                raise serializers.ValidationError("순서 정렬형 문제는 answer(정답)가 필요합니다.")

        elif q_type == "ox":
            if data.get("answer") not in ["O", "X", "o", "x", True, False, "true", "false"]:
                raise serializers.ValidationError("OX 퀴즈 정답은 'O' 또는 'X', true/false 형식이어야 합니다.")
        else:
            raise serializers.ValidationError(f"지원하지 않는 문제 유형입니다: {q_type}")

        return data






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
