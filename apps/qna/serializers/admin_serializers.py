from rest_framework import serializers

from apps.qna.models import Answer, Question, QuestionCategory, QuestionImage


# 질문 이미지
class AdminQuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


class AdminAnswerSerializer(serializers.ModelSerializer[Answer]):
    class Meta:
        model = Answer
        fields = ["id", "content", "author", "is_adopted", "created_at"]


# 카테고리 목록 조회
class AdminCategoryListSerializer(serializers.ModelSerializer[QuestionCategory]):
    type = serializers.CharField(read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "type", "created_at", "updated_at"]


# 질문 목록 조회
class AdminQuestionListSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]


# 질의 응답 상세 조회
class AdminQuestionDetailSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)
    answers = AdminAnswerSerializer(many=True, read_only=True)
    category = AdminCategoryListSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "author",
            "category",
            "view_count",
            "created_at",
            "updated_at",
            "images",
            "answers",
            "category",
        ]


# 질의응답 카테고리 질문 등록
class AdminCategoryCreateSerializer(serializers.ModelSerializer[QuestionCategory]):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        """카테고리명 중복 검증"""
        parent = self.initial_data.get("parent")

        # 같은 부모 하에서 동일한 이름의 카테고리가 있는지 확인
        if QuestionCategory.objects.filter(name=value, parent=parent).exists():
            raise serializers.ValidationError("같은 레벨에 동일한 이름의 카테고리가 이미 존재합니다.")

        return value

    def validate_parent(self, value):
        """부모 카테고리 검증"""
        if value:
            # 3단계 이상 깊이 방지 (대분류 > 중분류 > 소분류만 허용)
            if value.parent is not None and value.parent.parent is not None:
                raise serializers.ValidationError("카테고리는 최대 3단계까지만 생성할 수 있습니다.")

        return value


# class AdminCategoryCreateSerializer(serializers.ModelSerializer[QuestionCategory]):
#     type = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = QuestionCategory
#         fields = ["id", "name", "parent", "type", "created_at", "updated_at"]
#         read_only_fields = ["id", "created_at", "updated_at"]

# 추후 카테고리 검증 코드 추가 예정
# 검증 된 데이터로 생성 코드 구현 예정
