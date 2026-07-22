import redis.asyncio as redis_asyncio

from app.core.config import settings

redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"


def create_redis_client() -> redis_asyncio.Redis:
    """One client per process, attached to ``app.state.redis`` at startup.

    Every caller (``rate_limit.py``, ``token_denylist.py``) already treats a
    missing/unreachable client as "fail open" — this factory doesn't need to
    guard against connection errors itself, just needs to exist and be
    reachable eventually for those features to actually take effect.
    """
    return redis_asyncio.from_url(redis_url)
