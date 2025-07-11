from rest_framework import serializers

from apps.qna.models import (
    Answer,
    AnswerComment,
    AnswerImage,
    Question,
    QuestionAIAnswer,
    QuestionCategory,
    QuestionImage,
)


# 프로필 썸네일 이미지 serializer
class AdminProfileThumbnailSerializer(serializers.Serializer):
    profile_image = serializers.CharField(allow_null=True)


# 유저 닉네임 serializer
class AdminUserNicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField()


# 질문 작성자 정보 (상세 조회용)
class AdminQuestionDetailAuthorSerializer(serializers.Serializer):
    profile_thumbnail = AdminProfileThumbnailSerializer(read_only=True)
    nickname = serializers.CharField()
    position = serializers.CharField(allow_null=True)


# 질문 이미지 정보
class AdminQuestionDetailImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url"]


# 답변 이미지 정보
class AdminAnswerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerImage
        fields = ["id", "img_url"]


# 답변 댓글 정보
class AdminAnswerCommentSerializer(serializers.ModelSerializer):
    author = AdminUserNicknameSerializer(read_only=True)

    class Meta:
        model = AnswerComment
        fields = ["id", "author", "content", "created_at", "updated_at"]


# 일반 수강생 답변 정보
class AdminGeneralAnswerSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    images = AdminAnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "author", "content", "images", "is_adopted", "created_at", "updated_at"]

    def get_author(self, obj):
        if obj.author:
            return {
                "profile_thumbnail": {"profile_image": getattr(obj.author, "profile_image_url", None)},
                "nickname": obj.author.nickname,
                "position": getattr(obj.author, "position", None),
            }
        return None


# 조교 답변 정보
class AdminTutorAnswerSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    images = AdminAnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "author", "content", "images", "created_at", "updated_at"]

    def get_author(self, obj):
        if obj.author:
            return {
                "profile_thumbnail": {"profile_image": getattr(obj.author, "profile_image_url", None)},
                "nickname": obj.author.nickname,
                "school": getattr(obj.author, "school", None),
            }
        return None


# 운영매니저, 러닝코치, 어드민 답변 정보
class AdminStaffAnswerSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    images = AdminAnswerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "author", "content", "images", "created_at", "updated_at"]

    def get_author(self, obj):
        if obj.author:
            return {
                "profile_thumbnail": {"profile_image": getattr(obj.author, "profile_image_url", None)},
                "nickname": obj.author.nickname,
                "position": getattr(obj.author, "position", None),
            }
        return None


# 답변 목록 정보 (답변 유형별로 분류)
class AdminAnswerListSerializer(serializers.Serializer):
    general_answers = AdminGeneralAnswerSerializer(many=True, read_only=True)
    tutor_answers = AdminTutorAnswerSerializer(many=True, read_only=True)
    staff_answers = AdminStaffAnswerSerializer(many=True, read_only=True)


# AI 답변 정보
class AdminAIAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAIAnswer
        fields = ["id", "content", "created_at", "updated_at"]


# 카테고리 정보 (경로명은 serializer에서 구성)
class AdminQuestionCategorySerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()


# 질문 상세 조회 응답 serializer
class AdminQuestionDetailSerializer(serializers.ModelSerializer):
    author = AdminQuestionDetailAuthorSerializer(read_only=True)
    category = AdminQuestionCategorySerializer(read_only=True)
    images = AdminQuestionDetailImageSerializer(many=True, read_only=True)
    ai_answers = AdminAIAnswerSerializer(many=True, read_only=True)
    answers = AdminAnswerListSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "author",
            "category",
            "view_count",
            "images",
            "ai_answers",
            "answers",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.author:
            data["author"] = {
                "profile_thumbnail": {"profile_image": getattr(instance.author, "profile_image_url", None)},
                "nickname": instance.author.nickname,
                "position": getattr(instance.author, "position", None),
            }

        data["category"] = (
            {"category_id": instance.category.id, "category_name": self._build_category_path(instance.category)}
            if instance.category
            else None
        )

        answers = instance.answers.select_related("author").prefetch_related("images", "comments__author")
        general_answers, tutor_answers, staff_answers = [], [], []

        for answer in answers:
            role = getattr(answer.author, "role", "").upper() if answer.author else ""
            if role == "TA":
                tutor_answers.append(answer)
            elif role in ["OM", "LC", "ADMIN"]:
                staff_answers.append(answer)
            else:
                general_answers.append(answer)

        data["answers"] = {
            "general_answers": AdminGeneralAnswerSerializer(general_answers, many=True).data,
            "tutor_answers": AdminTutorAnswerSerializer(tutor_answers, many=True).data,
            "staff_answers": AdminStaffAnswerSerializer(staff_answers, many=True).data,
        }

        return data

    def _build_category_path(self, category):
        names = []
        while category:
            names.append(category.name)
            category = category.parent
        return " > ".join(reversed(names))


# 질문 이미지
class AdminQuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ["id", "img_url", "created_at", "updated_at"]
        read_only_fields = fields


class AdminAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "content", "author", "is_adopted", "created_at"]


# 질문 + 답변 통합 질의응답 상세 조회
class AdminQnADetailSerializer(serializers.Serializer):
    question = AdminQuestionDetailSerializer()
    answers = AdminAnswerSerializer(many=True)

    class Meta:
        ref_name = "AdminQnADetail"


# 카테고리 목록 조회
class AdminCategoryListSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source="id", read_only=True)
    parent_category_id = serializers.IntegerField(source="parent.id", read_only=True)
    category_name = serializers.CharField(source="name", read_only=True)
    category_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = QuestionCategory
        fields = ["category_id", "parent_category_id", "category_name", "category_type", "created_at", "updated_at"]


<<<<<<< Updated upstream
# 질문 목록 조회
class AdminQuestionListSerializer(serializers.ModelSerializer[Question]):
    images = AdminQuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "title", "content", "author", "category", "view_count", "created_at", "updated_at", "images"]
=======
# 작성자 정보
class AdminQuestionAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()


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
        data["author"] = {"id": instance.author.id, "nickname": instance.author.nickname} if instance.author else None
        data["category"] = (
            {"category_id": instance.category.id, "category_name": self._build_category_path(instance.category)}
            if instance.category
            else None
        )
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
>>>>>>> Stashed changes


# 질의응답 카테고리 질문 등록
class AdminCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "parent", "category_type", "created_at", "updated_at"]
        read_only_fields = ["id", "category_type", "created_at", "updated_at"]

    def validate_name(self, value):
        parent = self.initial_data.get("parent")
        if parent in ["", None, 0, "0"]:
            parent = None
        if QuestionCategory.objects.filter(name__iexact=value, parent=parent).exists():
            raise serializers.ValidationError("같은 레벨에 동일한 이름의 카테고리가 이미 존재합니다.")
        return value

    def validate_parent(self, value):
        if value:
            if value.category_type == "minor":
                raise serializers.ValidationError("카테고리는 최대 3단계까지만 생성할 수 있습니다.")
        return value

    def to_internal_value(self, data):
        if str(data.get("parent")) == "0":
            data["parent"] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        parent = validated_data.get("parent")
        if parent is None:
            validated_data["category_type"] = "major"
        elif parent.parent is None:
            validated_data["category_type"] = "middle"
        else:
            validated_data["category_type"] = "minor"
        return super().create(validated_data)
