import os

from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # +15005550006 (trial)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms_verification_code(phone_number: str, code: str) -> str:
    message = client.messages.create(
        body=f"[OZ] 인증번호는 [{code}]입니다.",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number,
    )
    return message.sid


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
