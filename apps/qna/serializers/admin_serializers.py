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
    category_id = serializers.IntegerField(source="id", read_only=True)
    parent_category_id = serializers.IntegerField(source="parent.id", read_only=True)
    category_name = serializers.CharField(source="name", read_only=True)
    category_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["category_id", "parent_category_id", "category_name", "category_type", "created_at", "updated_at"]


# 작성자 정보
class AdminQuestionAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()


# 카테고리 정보 (경로명은 serializer에서 구성)
class AdminQuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name"]

# 질문 목록 조회용
class AdminQuestionListSerializer(serializers.ModelSerializer):
    author = AdminQuestionAuthorSerializer(read_only=True)
    category = AdminQuestionCategorySerializer(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)
    has_answer = serializers.BooleanField(read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "author",
            "category",
            "view_count",
            "answer_count",
            "has_answer",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # 작성자
        data["author"] = {"id": instance.author.id, "nickname": instance.author.nickname} if instance.author else None

        # 카테고리 경로 구성
        data["category"] = (
            {"category_id": instance.category.id, "category_name": self._build_category_path(instance.category)}
            if instance.category
            else None
        )

        # DB에서 annotate로 받은 값 그대로 사용
        data["answer_count"] = instance.answer_count
        data["has_answer"] = instance.has_answer

        return data

    def _build_category_path(self, category):
        names = []
        while category:
            names.append(category.name)
            category = category.parent
        return " > ".join(reversed(names))


# 페이지네이션 응답 구조
class AdminQuestionListPaginationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = AdminQuestionListSerializer(many=True)


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
class AdminCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "category_type", "created_at", "updated_at"]
        read_only_fields = ["id", "category_type", "created_at", "updated_at"]

    def validate_name(self, value):
        # 카테고리명 중복 검증 (대소문자 구분 없이)
        parent = self.initial_data.get("parent")
        if parent in ["", None, 0, "0"]:
            parent = None

        if QuestionCategory.objects.filter(name__iexact=value, parent=parent).exists():
            raise serializers.ValidationError("같은 레벨에 동일한 이름의 카테고리가 이미 존재합니다.")
        return value

    def validate_parent(self, value):
        # 부모 카테고리 검증 및 3단계 제한
        if value:
            if value.category_type == "minor":
                raise serializers.ValidationError("카테고리는 최대 3단계까지만 생성할 수 있습니다.")
        return value

    def to_internal_value(self, data):
        # parent=0 → None으로 변환
        if str(data.get("parent")) == "0":
            data["parent"] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        # 카테고리 생성 시 category_type 자동 설정
        parent = validated_data.get("parent")

        if parent is None:
            # 대분류
            validated_data["category_type"] = "major"
        elif parent.parent is None:
            # 중분류
            validated_data["category_type"] = "middle"
        else:
            # 소분류
            validated_data["category_type"] = "minor"

        return super().create(validated_data)
