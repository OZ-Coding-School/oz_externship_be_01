from apps.users.tasks import send_verification_email_task
from apps.users.utils.base62 import generate_base62_code


def send_verification_code_to_email(email: str) -> str:
    code = generate_base62_code()
    send_verification_email_task.delay(email, code)
    return code
