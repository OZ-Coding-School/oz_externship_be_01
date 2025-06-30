import random


def send_verification_code_to_email(email: str) -> str:
    code = f"{random.randint(100000, 999999)}"
    # Gmail SMTP 발송 로직 추가
    return code
