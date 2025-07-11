from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.courses.models import Generation
from apps.tests.models import Test, TestDeployment, TestSubmission


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
            attrs["test"] = get_object_or_404(Test, id=test_id)
        elif chart_type == "score_by_subject":
            generation_id = attrs.get("generation_id")
            if not generation_id:
                raise serializers.ValidationError("score_by_subject 통계에는 generation_id가 필요합니다.")
            attrs["generation"] = get_object_or_404(Generation, id=generation_id)
        return attrs

    # 유형별 응답 데이터 반환
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
        # 기수별로 제출된 점수를 분류하여 평균 계산용으로 그룹핑
        generation_scores = {}
        for submission in submissions:
            generation = submission.deployment.generation
            gen_key = generation.id
            # 저장된 score 사용
            score = submission.score
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

        return {"type": "average_by_generation", "test_title": test.title, "data": result_data}

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

            # snapshot 없이 저장된 점수 사용
            score = submission.score

            # 응시 시간(분) 계산 = 제출 시각 - 시작 시각
            elapsed_minutes = int((submission.created_at - submission.started_at) / timedelta(minutes=1))
            results.append(
                {
                    "student_id": submission.student.id,
                    "score": score,
                    "elapsed_minutes": elapsed_minutes,
                }
            )

        return {"type": "score_vs_time", "test_title": test.title, "data": results}

    # 과목별 평균 점수 계산
    def handle_score_by_subject(self):
        # 요청된 기수(generation) 기준으로 모든 시험 배포 가져오기
        generation = self.validated_data["generation"]
        deployments = TestDeployment.objects.filter(generation=generation).select_related("test__subject")

        # 해당 배포에 대한 응시 기록 가져오기
        submissions = TestSubmission.objects.filter(deployment__in=deployments).select_related("student")
        # 과목별 점수 그룹핑 (저장된 점수 필드 사용)
        subject_scores = {}
        for submission in submissions:
            test = submission.deployment.test
            # 테스트 또는 과목이 없으면 스킵
            if not test or not test.subject:
                continue
            subject = test.subject
            subject_key = subject.id
            # 저장된 점수 필드 사용
            score = submission.score
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

        return {"type": "score_by_subject", "generation": f"{generation.number}기", "data": result_data}
