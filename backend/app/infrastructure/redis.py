import redis.asyncio as redis_asyncio

from app.core.config import settings

redis_url = settings.REDIS_URL or (
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)


def create_redis_client() -> redis_asyncio.Redis:
    return redis_asyncio.from_url(redis_url)
