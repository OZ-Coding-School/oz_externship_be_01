import random

from django.conf import settings
from django.core.mail import send_mail


def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))


def send_verification_code_to_email(email: str) -> str:
    code = generate_verification_code()
    send_mail(
        subject="[OZ] 회원가입 이메일 인증 코드입니다.",
        message=f"인증 코드는 {code} 입니다.",
        from_email=settings.EMAIL_HOST_USER,  # .local.env 에 작성해둠.
        recipient_list=[email],
        fail_silently=False,
    )
    return code
