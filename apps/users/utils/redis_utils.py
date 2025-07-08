import os

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def save_phone_code(phone: str, code: str, ttl: int = 300):
    r.setex(f"verify:phone:{phone}", ttl, code)


def get_phone_code(phone: str) -> str | None:
    code = r.get(f"verify:phone:{phone}")
    return code.decode() if code else None


def store_email_code(email: str, code: str, ttl: int = 300):
    r.setex(f"verify:email:{email}", ttl, code)


def get_stored_email_code(email: str) -> str | None:
    code = r.get(f"verify:email:{email}")
    return code.decode() if code else None


def mark_phone_verified(phone: str, ttl: int = 300):
    r.setex(f"phone_verified:{phone}", ttl, "true")


def is_phone_verified(phone: str) -> bool:
    value = r.get(f"phone_verified:{phone}")
    return value == b"true"
