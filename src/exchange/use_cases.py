import uuid
from dataclasses import asdict
from random import randint
import ujson
from fastapi.params import Depends
from redis import Redis
from tenacity import retry, wait_exponential_jitter, retry_if_exception_type, stop_after_attempt
from src.exchange.exceptions import NotFoundByNameError, CacheNotSavedError
from src.exchange.redis_client import get_redis
from src.binance.binance_price_service import BinancePriceService
from src.exchange.exchange_entities import Exchange
from src.exchange.interface import IExchangeRepo


class CreateExchangeMetricsUseCase:

    def __init__(self, repo: IExchangeRepo, binance_service: BinancePriceService):
        self.repo = repo
        self.binance_service = binance_service


    async def create_exchange_metrics(self, exchange_name: str) -> Exchange:

        prices = await self.binance_service.get_prices()

        new_exchange = Exchange(
            id=uuid.uuid4(),
            exchange_name=exchange_name,
            trust_score=randint(0, 10),
            btc_price=prices["BTCUSDT"],
            eth_price=prices["ETHUSDT"],
            sol_price=prices["SOLUSDT"]
        )

        await self.repo.create(new_exchange)

        return new_exchange



class GetExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, redis: Redis = Depends(get_redis)):
        self.repo = repo
        self.redis = redis


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=5),
        retry=retry_if_exception_type(CacheNotSavedError),
        reraise=True

    )
    async def save_to_cache(self, exchange_key: str, data: str, ex: int):
        await self.redis.set(exchange_key, data, ex)

        status_check = await self.redis.exists(exchange_key)
        if not status_check:
            raise CacheNotSavedError("Данные не добавились в кеш")


    async def get_exchange_by_name(self, exchange_name: str) -> Exchange:
        exchange_key = f"exchange_{exchange_name}"
        cached_data = await self.redis.get(exchange_key)
        if cached_data:
            data_dict = ujson.loads(cached_data)
            return Exchange(**data_dict)

        exchange = await self.repo.get_by_name(exchange_name)

        if not exchange:
            raise NotFoundByNameError(object_name=exchange_name, object_type='Exchange')

        exchange_dict = asdict(exchange)
        exchange_dict['id'] = str(exchange_dict['id'])
        data = ujson.dumps(exchange_dict)

        await self.save_to_cache(exchange_key=exchange_key, data=data, ex=3600)

        return exchange


class DeleteExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, redis: Redis = Depends(get_redis)):
        self.repo = repo
        self.redis = redis

    async def delete_exchange_info(self, exchange_name: str) -> None:
        exchange = self.repo.get_by_name(exchange_name=exchange_name)

        if exchange:
            await self.repo.delete_by_name(exchange_name=exchange_name)

        exchange_key = f"exchange_{exchange_name}"
        await self.redis.delete(exchange_key)
