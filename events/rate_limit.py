from django.conf import settings
from django.core.cache import cache


def _cache_key(action, identity):
    return f"rl:{action}:{identity}"


def is_rate_limited(action, identity, limit, window_seconds):
    if not settings.ENABLE_RATE_LIMITING:
        return False

    key = _cache_key(action, identity)
    count = cache.get(key, 0)
    if count >= limit:
        return True
    if count == 0:
        cache.set(key, 1, timeout=window_seconds)
    else:
        cache.incr(key)
    return False
