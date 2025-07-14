from django_redis import get_redis_connection  # type: ignore

redis = get_redis_connection("default")


def get_ai_count(session_key: str) -> int:
    return int(redis.get(f"ai_count:{session_key}") or 0)


def increment_ai_count(session_key) -> None:
    key = f"ai_count:{session_key}"
    count = redis.incr(key)

    # 새로 만든 키 만료 시간 설정 (기존 키 x)
    if count == 1:
        redis.expire(key, 60 * 60 * 24)
