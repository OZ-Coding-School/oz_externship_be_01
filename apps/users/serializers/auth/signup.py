from datetime import date
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from apps.users.utils.redis import is_phone_verified
from apps.users.models import User
from django_redis import get_redis_connection


class SignUpSerializer(serializers.ModelSerializer[Any]):
    password_confirm = serializers.CharField(write_only=True)
    birthday = serializers.DateField(default=date(2000, 1, 1))

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
            "profile_image_url",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "self_introduction": {"required": False, "allow_null": True},
            "profile_image_url": {"required": False, "allow_null": True},
        }

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value

    def validate_nickname(self, value: str) -> str:
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        return value

    def validate_phone_number(self, value: str) -> str:
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("이미 존재하는 휴대폰 번호입니다.")

        if not is_phone_verified(value):
            raise serializers.ValidationError("휴대폰 인증이 완료되지 않았습니다.")

        return value



    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:

        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        try:
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    # 가입 성공시 인증 상태 제거.
    def delete_phone_verification(phone: str) -> None:
        redis = get_redis_connection("default")
        redis.delete(f"phone:verified:{phone}")
