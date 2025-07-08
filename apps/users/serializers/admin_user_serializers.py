from typing import Any, Optional, Sequence

from rest_framework import serializers

from apps.courses.models import Course, Generation
from apps.users.models import User


# 목록 전용 시리얼라이저
class AdminUserListSerializer(serializers.ModelSerializer[User]):
    # 실제 DB는 created_at이지만 의미를 명확히 하기 위해 응답 필드명을 분리
    joined_at = serializers.DateTimeField(source="created_at", read_only=True)
    withdrawal_requested_at = serializers.DateTimeField(
        source="withdrawals.created_at", read_only=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "birthday",
            "role",
            "is_active",
            "joined_at",
            "withdrawal_requested_at",
        ]


# 디테일 시리얼라이저
class AdminUserDetailSerializer(serializers.ModelSerializer):
    # 공통 필드
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "gender",
            "nickname",
            "birthday",
            "phone_number",
            "email",
            "role",
            "is_active",
            "created_at",
            "profile_image_url",
        ]

    # 권한 별로 보여주는 필드 다르게 설정
    def to_representation(self, instance: User) -> dict:
        base = super().to_representation(instance)

        if instance.role == "TA":
            ta_permission = instance.ta_permissions.first()
            base["assigned_generation"] = (
                {
                    "course": ta_permission.generation.course.name,
                    "generation": ta_permission.generation.number,
                }
                if ta_permission
                else None
            )

        elif instance.role in {"OM", "LC"}:
            base["assigned_courses"] = [
                {
                    "course": perm.course.name,
                    "course_id": perm.course.id,
                }
                for perm in instance.staff_permissions.all()
            ]

        elif instance.role == "STUDENT":
            base["enrolled_generations"] = [
                {
                    "course": perm.generation.course.name,
                    "generation": perm.generation.number,
                }
                for perm in instance.student_permissions.all()
            ]

        return base


# 수정 등 기본 시리얼라이저
class AdminUserSerializer(serializers.ModelSerializer[User]):
    profile_image_file = serializers.ImageField(write_only=True)
    profile_image_url = serializers.URLField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "last_login",
            "password",
            "email",
            "role",
        ]

    # def validate(self, attrs):
    #     img_file = attrs.pop("profile_image_file")
    #     # 여기에 이미지 저장 로직.
    #     return super().validate(attrs)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # 사용자가 fields 키워드로 필드 제한할 수 있도록 허용
        fields: Optional[Sequence[str]] = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# 어드민 회원 권한 변경 시리얼라이저
class AdminUserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)
    generation = serializers.PrimaryKeyRelatedField(queryset=Generation.objects.all(), required=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False)


# 페이지네이션 시리얼라이저
class PaginatedAdminUserListSerializer(serializers.Serializer[dict[str, Any]]):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = AdminUserListSerializer(many=True)
