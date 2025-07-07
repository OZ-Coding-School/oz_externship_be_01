import logging
from datetime import date

from celery import shared_task  # type: ignore
from django.conf import settings
from django.core.mail import send_mail

from apps.users.models.withdrawals import Withdrawal

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_verification_email_task(self, email: str, code: str) -> None:
    try:
        send_mail(
            subject="[OZ] 회원가입 이메일 인증 코드입니다.",
            message=f"인증 코드는 {code} 입니다.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exception:
        logger.warning(f"[재시도] 이메일 전송 실패: {email}/사유: {exception}")
        raise self.retry(exc=exception)


# 14일이 지난 계정들 매일 정오에 자동으로 삭제
@shared_task
def delete_expired_withdrawn_users():
    today = date.today()
    expired_withdrawals = Withdrawal.objects.filter(due_date__lte=today)

    count = 0
    for withdrawal in expired_withdrawals:
        user = withdrawal.user
        logger.info(f"[Celery] 탈퇴 유예 기간이 만료된 사용자 삭제: {user.email} (ID: {user.id})")

        user.delete()
        withdrawal.delete()
        count += 1

    logger.info(f"[Celery] 탈퇴 유예 기간이 지난 사용자 {count}명 삭제")
