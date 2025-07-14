from datetime import date
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from rest_framework import serializers

from apps.users.models import User
from apps.users.utils.redis_utils import (
    is_phone_verified,
    is_signup_email_verified,
)
from core.utils.s3_file_upload import S3Uploader


def normalize_phone_number(phone: str) -> str:
    # 전화 번호 사이 - 빼버리기.
    return phone.replace("-", "").strip()


def is_valid_phone_format(phone: str) -> bool:
    # 010 으로 시작 하는지, 숫자 11자리 맞는지 검사.
    phone = normalize_phone_number(phone)
    return phone.startswith("010") and len(phone) == 11 and phone.isdigit()


class SignUpSerializer(serializers.ModelSerializer[Any]):
    password_confirm = serializers.CharField(write_only=True)
    birthday = serializers.DateField(default=date(2000, 1, 1))
    profile_image_file = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "name",
            "nickname",
            "gender",
            "phone_number",
            "birthday",
            "self_introduction",
            "profile_image_file",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "self_introduction": {"required": False, "allow_null": True},
            "profile_image_file": {"write_only": True, "required": False},
        }

    def validate_email(self, value):  # 중복 이메일
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일입니다.")
        if not is_signup_email_verified(value):
            raise serializers.ValidationError("이메일 인증이 완료되지 않았습니다.")
        return value

    def validate_nickname(self, value):  # 중복 닉네임
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        return value

    def validate_phone_number(self, value):  # 중복 + 인증 여부
        normalized = normalize_phone_number(value)

        if not is_valid_phone_format(value):
            raise serializers.ValidationError("휴대폰 번호 형식이 올바르지 않습니다. (예: 01012345678)")

        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError("이미 존재하는 휴대폰 번호입니다.")

        if not is_phone_verified(normalized):
            raise serializers.ValidationError("휴대폰 인증이 완료되지 않았습니다.")

        return normalized

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        pw, pw2 = attrs.get("password"), attrs.pop("password_confirm", None)
        if pw != pw2:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        try:
            validate_password(pw)
        except ValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):

        email = validated_data.get("email")
        phone = validated_data.get("phone_number")

        if not is_signup_email_verified(email):
            raise ValidationError("이메일 인증이 완료되지 않았습니다.")

        normalized_phone = normalize_phone_number(phone)
        if not is_phone_verified(normalized_phone):
            raise ValidationError("휴대폰 인증이 완료되지 않았습니다.")


        profile_image_file = validated_data.pop("profile_image_file", None)
        if profile_image_file:
            s3_uploader = S3Uploader()
            file_url = s3_uploader.upload(file=profile_image_file, directory="profile_images")
            validated_data["profile_image_url"] = file_url

        validated_data["phone_number"] = normalize_phone_number(validated_data["phone_number"])

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SignupNicknameCheckSerializer(serializers.Serializer[dict[str, Any]]):
    nickname = serializers.CharField()

    def validate_nickname(self, value: str) -> str:
        if value == "existing_nickname":
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value
