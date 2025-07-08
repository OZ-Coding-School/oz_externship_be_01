import os

from django.conf import settings
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # +15005550006 (trial)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms_verification_code(phone_number: str) -> str:
    verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
        to=phone_number, channel="sms"
    )
    return verification.status


def check_verification_code(phone_number: str, code: str):
    verification_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
        to=phone_number, code=code
    )
    return verification_check.status


def normalize_phone_number(phone: str) -> str:
    # 숫자만 남기기
    phone = phone.replace("-", "").replace(" ", "").strip()

    # 국내 번호일 경우 국제 포맷으로 변환
    if phone.startswith("010"):
        return "+82" + phone[1:]
    elif phone.startswith("011"):
        return "+82" + phone[1:]
    elif phone.startswith("+82"):
        return phone
    else:
        raise ValueError("지원되지 않는 전화번호 형식입니다.")
