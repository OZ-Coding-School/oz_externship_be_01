from django_redis import get_redis_connection  # type: ignore


def store_email_code(email: str, code: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"email:{email}", code, ex=300)


def get_stored_email_code(email: str) -> str | None:
    redis = get_redis_connection("default")
    code = redis.get(f"email:{email}")
    return code.decode("utf-8") if code else None
