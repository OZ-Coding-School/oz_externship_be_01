from rest_framework import serializers
from apps.qna.models import QuestionCategory, Answer, Question


# 질의응답 카테고리 질문 등록
class AdminCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "created_at", "updated_at"]

    def validate(self, data):
        if data.get("type") == "대" and data.get("parent_id"):
            raise serializers.ValidationError("대분류는 parent_id를 지정할 수 없습니다.")
        if data.get("type") != "대" and not data.get("parent_id"):
            raise serializers.ValidationError("중분류 또는 소분류는 parent_id를 지정해야 합니다.")
        return data

    def create(self, validated_data):
        category = QuestionCategory.objects.create(**validated_data)
        return category

# 질의응답 카테고리 질문 삭제
class AdminCategoryDeleteResponseSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    detail = serializers.SerializerMethodField()

    def validate(self, data):
        try:
            QuestionCategory.objects.get(id=data["category_id"])
        except QuestionCategory.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 질문입니다.")
        return data

# 답변 삭제
class AdminAnswerDeleteSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField()
    detail = serializers.CharField()

    def validate(self, data):
        try:
            Answer.objects.get(id=data["answer_id"])
        except Answer.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 답변입니다.")
        return data

# 질문 삭제
class AdminQuestionDeleteSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField()
    detail = serializers.CharField()

    def validate(self, data):
        try:
            Question.objects.get(id=data["question_id"])
        except Question.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 질문입니다.")
        return data

# 질의응답 상세 조회
# 질문 목록 조회
# 징의응답 카테고리 목록 조회