from typing import Any

from rest_framework import serializers


# 닉네임 중복체크
class NicknameCheckSerializer(serializers.Serializer[dict[str, Any]]):
    nickname = serializers.CharField()

    def validate_nickname(self, value: str) -> str:
        if value == "existing_nickname":
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value


# 프로필 확인
class UserProfileSerializer(serializers.Serializer[dict[str, Any]]):
    profile_image_url = serializers.CharField(allow_null=True)
    email = serializers.EmailField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    phone_number = serializers.CharField()
    birthday = serializers.DateField()
    course_name = serializers.CharField(required=False)
    generation = serializers.CharField(required=False)


# 프로필 수정
class UserProfileUpdateSerializer(serializers.Serializer[dict[str, Any]]):
    profile_image_file = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    nickname = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        password = data.get("password")
        password2 = data.get("password2")

        if password or password2:
            if password != password2:
                raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
