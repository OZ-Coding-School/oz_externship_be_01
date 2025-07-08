from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.courses.models import Generation, Subject
from apps.tests.models import Test, TestDeployment, TestSubmission


# 문제 유형별 정답 비교 함수 선언
def compare_answers(question_type, snapshot_answer, student_answer) -> bool:
    if question_type == "multiple_choice_single":
        return student_answer == snapshot_answer
    elif question_type == "multiple_choice_multi":
        return set(student_answer or []) == set(snapshot_answer or [])
    elif question_type == "ox":
        return str(student_answer).upper() == str(snapshot_answer).upper()
    elif question_type == "ordering":
        return student_answer == snapshot_answer
    elif question_type == "fill_in_blank":
        return student_answer == snapshot_answer
    elif question_type == "short_answer":
        return str(student_answer).strip().lower() == str(snapshot_answer).strip().lower()
    else:
        raise ValueError(f"지원하지 않는 문제 유형입니다: {question_type}")


# 스냅샷 기준 학생 제출 답안 채점
def calculate_submission_score(snapshot_json: dict, answers_json: dict) -> int:
    total_score = 0
    for question_id, question_data in snapshot_json.items():
        question_type = question_data.get("type")
        snapshot_answer = question_data.get("answer")
        point = question_data.get("point", 0)
        student_answer = answers_json.get(question_id)

        if compare_answers(question_type, snapshot_answer, student_answer):
            total_score += point
    return total_score


# 통계 대시보드 요청용 Serializer
class DashboardSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["average_by_generation", "score_vs_time", "score_by_subject"])
    test_id = serializers.IntegerField(required=False)
    generation_id = serializers.IntegerField(required=False)

    # 요청 검증 및 DB 객체 주입
    def validate(self, attrs):
        chart_type = attrs["type"]

        if chart_type in ["average_by_generation", "score_vs_time"]:
            test_id = attrs.get("test_id")
            if not test_id:
                raise serializers.ValidationError("해당 통계 유형에는 test_id가 필요합니다.")
            test = get_object_or_404(Test, id=test_id)
            attrs["test"] = test

        elif chart_type == "score_by_subject":
            generation_id = attrs.get("generation_id")
            if not generation_id:
                raise serializers.ValidationError("score_by_subject 통계에는 generation_id가 필요합니다.")
            generation = get_object_or_404(Generation, id=generation_id)
            attrs["generation"] = generation

        return attrs

    # 응답 데이터 반환
    def get_response_data(self):
        chart_type = self.validated_data["type"]
        if chart_type == "average_by_generation":
            return self.handle_average_by_generation()
        elif chart_type == "score_vs_time":
            return self.handle_score_vs_time()
        elif chart_type == "score_by_subject":
            return self.handle_score_by_subject()
        raise serializers.ValidationError("지원하지 않는 통계 유형입니다.")

    # 기수별 평균 점수 계산
    def handle_average_by_generation(self):
        test = self.validated_data["test"]

        # 해당 테스트에 대한 모든 배포 가져오기
        deployments = TestDeployment.objects.filter(test=test).select_related("generation")

        # 배포된 시험에 대한 모든 응시 기록 가져오기
        submissions = TestSubmission.objects.filter(deployment__in=deployments).select_related(
            "student", "deployment__generation"
        )

        generation_scores = {}  # {generation_id: {"generation": obj, "scores": [점수들]}}

        for submission in submissions:
            generation = submission.deployment.generation
            gen_key = generation.id
            snapshot_json = submission.deployment.questions_snapshot_json
            answers_json = submission.answers_json
            if not snapshot_json:
                continue

            # 제출 점수 계산
            score = calculate_submission_score(snapshot_json, answers_json)

            # 기수별 점수 누적합산
            generation_scores.setdefault(gen_key, {"generation": generation, "scores": []})["scores"].append(score)

        result_data = []
        for gen in generation_scores.values():
            scores = gen["scores"]
            avg_score = sum(scores) / len(scores) if scores else 0
            result_data.append(
                {
                    "generation": f"{gen['generation'].number}기",
                    "average_score": round(avg_score),
                }
            )

        return {
            "type": "average_by_generation",
            "test_title": test.title,
            "data": result_data,
        }

    # 응시 시간 대비 점수 산점도 생성
    def handle_score_vs_time(self):
        test = self.validated_data["test"]

        # 최근 5개 기수의 시험 배포 가져오기
        deployments = (
            TestDeployment.objects.filter(test=test).order_by("-generation__number").select_related("generation")[:5]
        )

        # 해당 배포의 모든 응시 기록 가져오기
        submissions = TestSubmission.objects.filter(deployment__in=deployments).select_related("student")

        results = []
        for submission in submissions:
            snapshot = submission.deployment.questions_snapshot_json
            answers = submission.answers_json
            if not snapshot:
                continue

            # 제출 점수 계산
            score = calculate_submission_score(snapshot, answers)

            # 응시 시간(분) 계산 = 제출 시각 - 시작 시각
            elapsed_minutes = int((submission.created_at - submission.started_at) / timedelta(minutes=1))

            results.append(
                {
                    "student_id": submission.student.id,
                    "score": score,
                    "elapsed_minutes": elapsed_minutes,
                }
            )

        return {
            "type": "score_vs_time",
            "test_title": test.title,
            "data": results,
        }

    # 과목별 평균 점수 계산
    def handle_score_by_subject(self):
        # 요청된 기수(generation) 기준으로 모든 시험 배포 가져오기
        generation = self.validated_data["generation"]
        deployments = TestDeployment.objects.filter(generation=generation).select_related("test__subject")

        # 해당 배포에 대한 응시 기록ㄱ 가져오기
        submissions = TestSubmission.objects.filter(deployment__in=deployments).select_related("student")

        subject_scores = {}  # {subject_id: {"subject": obj, "scores": [점수들]}}

        for submission in submissions:
            test = submission.deployment.test
            # 테스트 또는 과목이 없으면 스킵
            if not test or not test.subject:
                continue
            subject = test.subject
            subject_key = subject.id
            snapshot_json = submission.deployment.questions_snapshot_json
            answers_json = submission.answers_json
            if not snapshot_json:
                continue

            # 제출한 답안 기반으로 점수 계산
            score = calculate_submission_score(snapshot_json, answers_json)

            # 과목별 점수 리스트에 추가
            subject_scores.setdefault(subject_key, {"subject": subject, "scores": []})["scores"].append(score)

        result_data = []
        for sub in subject_scores.values():
            scores = sub["scores"]
            avg_score = sum(scores) / len(scores) if scores else 0
            result_data.append(
                {
                    "subject_title": sub["subject"].title,
                    "average_score": round(avg_score),
                }
            )

        return {
            "type": "score_by_subject",
            "generation": f"{generation.number}기",
            "data": result_data,
        }
