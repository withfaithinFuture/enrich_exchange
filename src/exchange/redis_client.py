from redis.asyncio import Redis


redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
# redis_client = Redis(host='redis_v2', port=6379, db=0, decode_responses=True)
async def get_redis():
    yield redis_client