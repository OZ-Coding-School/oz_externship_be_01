from django_redis import get_redis_connection  # type: ignore


# 이메일 인증 코드를 Redis에 저장. 시간은 5분.
def store_email_code(email: str, code: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"email:{email}", code, ex=300)


# redis 에서 이메일 인증 코드 조회.
def get_stored_email_code(email: str) -> str | None:
    redis = get_redis_connection("default")
    code = redis.get(f"email:{email}")
    return code.decode("utf-8") if code else None


# 이메일 인증 성공 시 인증 완료 상태를 Redis에 저장, 유효시간은 1시간 으로 설정.
def mark_email_as_verified(email: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"email:verified:{email}", "true", ex=3600)


# 이메일 인증 여부 확인.
def is_email_verified(email: str) -> bool:
    redis = get_redis_connection("default")
    return redis.get(f"email:verified:{email}") == b"true"

# ---------------------------------------------------------

# 휴대폰 인증 코드를 Redis에 저장 (5분)
def store_phone_code(phone: str, code: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"phone:{phone}", code, ex=300)

# Redis에서 휴대폰 인증 코드 조회
def get_stored_phone_code(phone: str) -> str | None:
    redis = get_redis_connection("default")
    code = redis.get(f"phone:{phone}")
    return code.decode("utf-8") if code else None

# 인증 성공 시 Redis에 인증 상태 저장 (1시간 유효)
def mark_phone_as_verified(phone: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"phone:verified:{phone}", "true", ex=3600)

# 인증 여부 조회
def is_phone_verified(phone: str) -> bool:
    redis = get_redis_connection("default")
    return redis.get(f"phone:verified:{phone}") == b"true"
