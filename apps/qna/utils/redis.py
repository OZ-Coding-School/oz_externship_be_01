import redis
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=1,
    decode_responses=True,
)


def get_ai_count(session_key: str) -> int:
    return int(redis_client.get(f"ai_count:{session_key}") or 0)


def increment_ai_count(session_key) -> None:
    key = f"ai_count:{session_key}"
    count = redis_client.incr(key)

    # 새로 만든 키 만료 시간 설정 (기존 키 x)
    if count == 1:
        redis_client.expire(key, 60 * 60 * 24)
