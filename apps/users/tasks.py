from celery import shared_task  # type: ignore
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_verification_email_task(email: str, code: str) -> None:
    send_mail(
        subject="[OZ] 회원가입 이메일 인증 코드입니다.",
        message=f"인증 코드는 {code} 입니다.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
