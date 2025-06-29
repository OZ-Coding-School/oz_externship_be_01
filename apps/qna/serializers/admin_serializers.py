from rest_framework import serializers

from apps.qna.models import Question, QuestionCategory, QuestionImage


# 질문 이미지
class AdminQuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


# 질문 목록 조회
class AdminQuestionListSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]


# 질문 상세 조회
class AdminQuestionDetailSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]


# 질의응답 카테고리 질문 등록
class AdminCategoryCreateSerializer(serializers.ModelSerializer[QuestionCategory]):
    type = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "type", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    # 추후 카테고리 검증 코드 추가 예정
    # 검증 된 데이터로 생성 코드 구현 예정


# 카테고리 목록 조회
class AdminCategoryListSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "name", "parent", "type", "created_at", "updated_at"]
