from typing import Any

from rest_framework.exceptions import ValidationError

from apps.tests.models import Test, TestQuestion


class QuestionValidator:
    def validate_multiple_choice_single_question(self, data: dict[str, Any]) -> dict[str, Any]:
        options = data.get("options_json")
        answer = data.get("answer")

        if not isinstance(options, list) or len(options) < 2:
            raise ValidationError("객관식은 options_json(보기)가 2개 이상 필요합니다.")
        if not isinstance(answer, list) or len(answer) != 1:
            raise ValidationError("단일 선택 객관식은 정답(answer)을 하나만 리스트로 입력해야 합니다.")

        if answer[0] not in options:
            raise ValidationError(f"정답 '{answer[0]}'이 보기 목록에 없습니다.")

        return data

    def validate_multiple_choice_multi_question(self, data: dict[str, Any]) -> dict[str, Any]:
        options = data.get("options_json")
        answer = data.get("answer")

        if not isinstance(options, list) or len(options) < 2:  # 다지 선다형이라 정답 2개 이상 적어야 통과
            raise ValidationError("객관식은 options_json(보기)가 2개 이상 필요합니다.")
        if not isinstance(answer, list) or len(answer) < 2:
            raise ValidationError("다중 선택 객관식은 두개 이상의 정답(answer)을 리스트로 입력해야 합니다.")

        invalid_answers = [a for a in answer if a not in options]  # 문제에 없는 정답 적으면 오류 출력
        if invalid_answers:
            raise ValidationError(f"다음 정답은 보기 목록에 없습니다: {invalid_answers}")

        return data

    def validate_short_answer_question(self, data: dict[str, Any]) -> dict[str, Any]:
        answer = data.get("answer")
        if not answer:
            raise ValidationError("주관식 단답형은 answer(정답)이 필요합니다.")

        data["options_json"] = None
        data["prompt"] = None
        data["blank_count"] = None

        return data

    def validate_ordering_question(self, data: dict[str, Any]) -> dict[str, Any]:
        options = data.get("options_json", [])
        answer = data.get("answer", [])

        if not isinstance(options, list) or len(options) < 2:
            raise ValidationError("순서 정렬형 문제는 최소 2개의 보기가 필요합니다.")

        if not isinstance(answer, list) or len(answer) != len(options):
            raise ValidationError("정답(answer)은 보기(options_json)와 동일한 개수여야 합니다.")

        if sorted(answer) != sorted(options):
            raise ValidationError("정답(answer)은 보기(options_json) 안에 있는 문제와 동일 해야합니다. ")

        data["prompt"] = None
        data["blank_count"] = None

        return data

    def validate_fill_in_blank_question(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data.get("prompt"):
            raise ValidationError("빈칸 채우기 문제는 prompt(지문)이 필요합니다.")
        if not data.get("blank_count") or data["blank_count"] < 1:
            raise ValidationError("빈칸 개수는 1개 이상이어야 합니다.")
        if not data.get("answer"):
            raise ValidationError("빈칸 채우기 문제는 answer(정답)이 필요합니다.")
        data["options_json"] = None

        return data

    def validate_ox_question(self, data: dict[str, Any]) -> dict[str, Any]:
        answer_list = data.get("answer")
        # answer는 반드시 문자열 형태로 하나의 값만 포함해야 함
        if not isinstance(answer_list, str):
            raise ValidationError("OX 퀴즈는 정답을 하나만 문자열로 입력해야 합니다.")
        # 정답 값 검증
        answer_value = answer_list[0]
        if answer_value not in ["O", "X", "o", "x"]:
            raise ValidationError("OX 퀴즈 정답은 'O' 또는 'X' 형식이어야 합니다.")
        # 필요 없는 필드 초기화
        data["options_json"] = None
        data["prompt"] = None
        data["blank_count"] = None

        return data

    def validate_point_field(self, test: Test, point: int) -> bool:
        # 배점 합산 제한 (쵀대 100점)
        current_total = sum(q.point for q in test.questions.all())
        if current_total + point > 100:
            raise ValidationError(" 총 배점은 100점을 초과할 수 없습니다.")
        return True

    def validate_questions_total_score(self, data: list[dict[str, Any]]) -> bool:
        total_score = 0
        for question in data:
            total_score += question["point"]
            if total_score > 100:
                raise ValidationError("총 배점은 100점을 초과할 수 없습니다.")
        return True

    def validatequestions_length_at_db(self, test: Test) -> bool:
        if test.questions.count() > 19:
            raise ValidationError("쪽지시험 당 최대 20문제까지만 등록할 수 있습니다.")
        return True

    def validate_questions_length(self, data: list[dict[str, Any]]) -> bool:
        if len(data) > 20:
            raise ValidationError("쪽지시험 당 최대 20문제까지만 등록할 수 있습니다.")
        return True

    def validate_question_by_type(self, data: dict[str, Any]) -> dict[str, Any]:
        q_type = data.get("type")

        if q_type == "fill_in_blank":
            return self.validate_fill_in_blank_question(data=data)

        # 다지선다형 문제
        elif q_type == "multiple_choice_single":  # 단일
            return self.validate_multiple_choice_single_question(data=data)

        elif q_type == "multiple_choice_multi":  # 다중
            return self.validate_multiple_choice_multi_question(data=data)

        # 주관식 단답형 문제
        elif q_type == "short_answer":
            return self.validate_short_answer_question(data=data)

        # 순서 정렬 문제
        elif q_type == "ordering":
            return self.validate_ordering_question(data=data)

        elif q_type == "ox":
            print(f"OX 문제 처리 필요, q_type 타입: {type(q_type)}")
            return self.validate_ox_question(data=data)

        else:
            raise ValidationError(f"문제 유형(type)은 {TestQuestion.QuestionType.choices} 중에서 선택해야합니다.")
