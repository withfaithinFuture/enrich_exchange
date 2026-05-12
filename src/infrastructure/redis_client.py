from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.exchanges.exceptions import CacheNotSavedError


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
async def get_redis():
    yield redis_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=5),
    retry=retry_if_exception_type((CacheNotSavedError, ConnectionError, TimeoutError)),
    reraise=True

)
async def save_to_cache(redis: Redis, exchange_key: str, data: str, ex: int):
    await redis.set(exchange_key, data, ex)
    status_check = await redis.exists(exchange_key)

    if not status_check:
        raise CacheNotSavedError("Данные не добавились в кеш")