from rest_framework import serializers


class GenerationAverageSerializer(serializers.Serializer):  # type: ignore
    generation = serializers.CharField(help_text="기수 (예: 1기)")
    average_score = serializers.IntegerField(help_text="해당 기수의 평균 점수")


class AverageByGenerationSerializer(serializers.Serializer):  # type: ignore
    type = serializers.ChoiceField(choices=["average_by_generation"])
    test_title = serializers.CharField(help_text="시험 제목")
    data: serializers.ListSerializer = GenerationAverageSerializer(many=True)  # type: ignore


class ScoreVsTimeDataSerializer(serializers.Serializer):  # type: ignore
    student_id = serializers.IntegerField(help_text="학생 ID")
    score = serializers.IntegerField(help_text="점수")
    elapsed_minutes = serializers.IntegerField(help_text="응시 시간(분)")


class ScoreVsTimeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    type = serializers.ChoiceField(choices=["score_vs_time"])
    test_title = serializers.CharField(help_text="시험 제목")
    data: serializers.ListSerializer = ScoreVsTimeDataSerializer(many=True)  # type: ignore


class SubjectScoreSerializer(serializers.Serializer):  # type: ignore[type-arg]
    subject = serializers.CharField(help_text="과목 이름")
    average_score = serializers.IntegerField(help_text="과목별 평균 점수")


class ScoreBySubjectSerializer(serializers.Serializer):  # type: ignore[type-arg]
    type = serializers.ChoiceField(choices=["score_by_subject"])
    generation = serializers.CharField(help_text="기수")
    data: serializers.ListSerializer = SubjectScoreSerializer(many=True)  # type: ignore
