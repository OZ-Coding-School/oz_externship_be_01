from typing import Any, Dict

from rest_framework import serializers


# 이메일 찾기
class EmailFindRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    name = serializers.CharField()
    phone_number = serializers.CharField()


# 이메일 찾기 응답
class EmailFindResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    email = serializers.CharField()


# 인증코드 발송
class PasswordResetEmailSendSerializer(serializers.Serializer[Dict[str, Any]]):
    email = serializers.EmailField()


# 인증코드 확인
class PasswordResetVerifyCodeSerializer(serializers.Serializer[Dict[str, Any]]):
    email = serializers.EmailField()
    code = serializers.CharField()


# 비밀번호 변경
class PasswordChangeRequestSerializer(serializers.Serializer[Dict[str, Any]]):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data
