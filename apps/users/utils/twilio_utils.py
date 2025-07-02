from twilio.rest import Client
from django.conf import settings
import os


def send_sms_code(phone_number: str, code: str) -> None:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_number:
        raise ValueError("Twilio 환경변수가 설정되지 않았습니다.")

    client = Client(account_sid, auth_token)

    normalized_phone = normalize_phone_number(phone_number)  # +8210...
    print(f"📤 Sending SMS to: {normalized_phone} from {from_number}")

    message = client.messages.create(
        to="+821075631482",
        from_="+16068872102",
        body=f"[OZ 인증] 본인인증 코드: {code}"
    )

    print(f"✅ SMS 전송 완료: {message.sid}")

def normalize_phone_number(phone_number: str) -> str:

    # 01012345678 → +821012345678 변경.
    phone_number = phone_number.strip().replace("-", "")
    if phone_number.startswith("0"):
        return "+82" + phone_number[1:]
    elif phone_number.startswith("+82"):
        return phone_number
    raise ValueError("잘못된 전화번호 형식입니다.")