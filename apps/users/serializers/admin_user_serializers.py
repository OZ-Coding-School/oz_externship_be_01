from typing import Any, Optional
from uuid import uuid4

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.courses.models import Course, Generation
from apps.users.models import PermissionsStudent
from apps.users.models import User
from core.utils.s3_file_upload import S3Uploader


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


# 수정 시리얼라이저
class AdminUserUpdateSerializer(serializers.ModelSerializer[User]):
    profile_image_file = serializers.ImageField(write_only=True, required=False)
    profile_image_url = serializers.URLField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["id", "created_at", "last_login", "password", "email", "role"]

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        profile_img_file: Optional[UploadedFile] = validated_data.pop("profile_image_file", None)

        if profile_img_file:
            uploader = S3Uploader()

            # 기존 이미지 삭제
            if instance.profile_image_url:
                uploader.delete_file(instance.profile_image_url)

            # 새 이미지 업로드
            ext = profile_img_file.name.split('.')[-1]
            s3_key = f"users/profile_images/user_{instance.id}_{uuid4().hex}.{ext}"
            s3_url = uploader.upload_file(profile_img_file, s3_key)

            if not s3_url:
                raise serializers.ValidationError("프로필 이미지 업로드에 실패했습니다.")

            instance.profile_image_url = s3_url

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



# 어드민 회원 권한 변경 시리얼라이저
class AdminUserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)
    generation = serializers.PrimaryKeyRelatedField(queryset=Generation.objects.all(), required=False)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False)

    def validate(self, attrs):
        role = attrs.get("role")
        generation = attrs.get("generation")
        course = attrs.get("course")
        user = self.context["target_user"]

        if role in [User.Role.STUDENT, User.Role.TA] and not generation:
            raise serializers.ValidationError("generation 필드는 필수입니다.")

        if role in [User.Role.OM, User.Role.LC] and not course:
            raise serializers.ValidationError("course 필드는 필수입니다.")

        if role == User.Role.STUDENT:
            if PermissionsStudent.objects.filter(user=user, generation=generation).exists():
                raise serializers.ValidationError("이미 해당 기수에 대한 수강 권한이 존재합니다.")

        return attrs


# 페이지네이션 시리얼라이저
class PaginatedAdminUserListSerializer(serializers.Serializer[dict[str, Any]]):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = AdminUserListSerializer(many=True)
