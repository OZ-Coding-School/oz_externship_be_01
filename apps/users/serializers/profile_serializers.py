from typing import Any

from rest_framework import serializers

from apps.courses.models import EnrollmentRequest
from apps.users.models import User
from apps.users.utils.redis_utils import is_phone_verified


# 닉네임 중복체크
class NicknameCheckSerializer(serializers.Serializer[dict[str, Any]]):
    nickname = serializers.CharField()

    def validate_nickname(self, value: str) -> str:
        if value == "existing_nickname":
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value


# 프로필 확인
class UserProfileSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    generation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "profile_image_url",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "course_name",
            "generation",
        ]

    def get_course_name(self, obj):
        if obj.role == User.Role.STUDENT:
            enrollment = (
                EnrollmentRequest.objects.filter(user=obj)
                .select_related("generation__course")
                .order_by("-created_at")
                .first()
            )
            return enrollment.generation.course.name if enrollment else None
        return None

    def get_generation(self, obj):
        if obj.role == User.Role.STUDENT:
            enrollment = (
                EnrollmentRequest.objects.filter(user=obj)
                .select_related("generation__course")
                .order_by("-created_at")
                .first()
            )
            return f"{enrollment.generation.number}기" if enrollment else None
        return None


# 프로필 수정
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_image_file = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    nickname = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "profile_image_file",
            "password",
            "password2",
            "nickname",
            "phone_number",
        ]

    # 닉네임
    def validate_nickname(self, value: str) -> str:
        user = self.context["request"].user
        if User.objects.exclude(id=user.id).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    # 휴대폰
    def validate_phone_number(self, value: str) -> str:
        user = self.context["request"].user

        if not is_phone_verified(value):
            raise serializers.ValidationError("휴대폰 번호 인증이 완료되지 않았습니다.")

        if User.objects.exclude(id=user.id).filter(phone_number=value).exists():
            raise serializers.ValidationError("이미 사용 중인 전화번호입니다.")

        return value

    # 비밀번호
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        password = data.get("password")
        password2 = data.get("password2")

        if password or password2:
            if password != password2:
                raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# 프로필 수정 응답
class UserProfileUpdateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    updated_fields = serializers.DictField(child=serializers.CharField(allow_null=True, allow_blank=True))
