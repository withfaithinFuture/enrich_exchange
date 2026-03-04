import uuid
from dataclasses import asdict
from random import randint
import ujson
from fastapi.params import Depends
from redis import Redis
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

    def __init__(self, repo: IExchangeRepo, create_use_case: CreateExchangeMetricsUseCase, redis: Redis = Depends(get_redis)):
        self.repo = repo
        self.create_use_case = create_use_case
        self.redis = redis


    async def get_exchange_by_name(self, exchange_name: str) -> Exchange:
        exchange_key = f"exchange_{exchange_name}"
        cached_data = await self.redis.get(exchange_key)
        if cached_data:
            data_dict = ujson.loads(cached_data)
            return Exchange(**data_dict)

        exchange = await self.repo.get_by_name(exchange_name)

        if not exchange:
            await self.create_use_case.execute(exchange_name)
            exchange = await self.repo.get_by_name(exchange_name)

        exchange_dict = asdict(exchange)
        exchange_dict['id'] = str(exchange_dict['id'])
        data = ujson.dumps(exchange_dict)

        await self.redis.set(exchange_key, data, ex=3600)

        return exchange