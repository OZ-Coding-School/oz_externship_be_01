from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


def is_nickname_duplicated(nickname: str, user_id: int | None = None) -> bool:
    key = f"nickname_check:{nickname.lower()}:{user_id or 'anon'}"
    cached = cache.get(key)
    if cached is not None:
        return cached

    qs = User.objects.filter(nickname=nickname)
    if user_id:
        qs = qs.exclude(id=user_id)
    duplicated = qs.exists()

    cache.set(key, duplicated, timeout=10)
    return duplicated
