import uuid
from dataclasses import asdict
from random import randint
import ujson
from redis import Redis

from src.exchanges.exceptions import NotFoundByNameError
from src.infrastructure.redis_client import get_redis, save_to_cache
from src.binance.binance_price_service import BinancePriceService
from src.exchanges.exchange_entities import Exchange
from src.exchanges.interface import IExchangeRepo


class CreateExchangeMetricsUseCase:

    def __init__(self, repo: IExchangeRepo, binance_service: BinancePriceService):
        self.repo = repo
        self.binance_service = binance_service


    async def map_prices(self, exchange: Exchange, fresh_prices: dict) -> Exchange:
        symbols = {
            "BTCUSDT": "btc_price",
            "ETHUSDT": "eth_price",
            "SOLUSDT": "sol_price"
        }

        for symbol, field in symbols.items():
            if hasattr(exchange, field):
                setattr(exchange, field, fresh_prices[symbol])

        return exchange


    async def create_exchange_metrics(self, exchange_name: str) -> Exchange:

        prices = await self.binance_service.get_prices()

        existing_exchange = await self.repo.get_by_name(exchange_name=exchange_name)
        if existing_exchange:
            await self.map_prices(exchange=existing_exchange, fresh_prices=prices)
            await self.repo.update(exchange=existing_exchange)
            return existing_exchange

        new_exchange = Exchange(
            id=uuid.uuid4(),
            exchange_name=exchange_name,
            trust_score=randint(0, 10),
            btc_price=prices["BTCUSDT"],
            eth_price=prices["ETHUSDT"],
            sol_price=prices["SOLUSDT"]
        )

        await self.repo.create(new_exchange)
        await self.repo.update(exchange=new_exchange)
        return new_exchange


class GetExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, redis: Redis):
        self.repo = repo
        self.redis = redis


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

        await save_to_cache(redis=self.redis, exchange_key=exchange_key, data=data, ex=3600)

        return exchange


class DeleteExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, redis: Redis):
        self.repo = repo
        self.redis = redis

    async def delete_exchange_info(self, exchange_name: str) -> None:
        exchange = await self.repo.get_by_name(exchange_name=exchange_name)

        if exchange:
            await self.repo.delete_by_name(exchange_name=exchange_name)

        exchange_key = f"exchange_{exchange_name}"
        await self.redis.delete(exchange_key)
