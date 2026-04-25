from fastapi import Depends

from exchanges.use_cases import DeleteExchangeUseCase
from src.binance.binance_price_service import BinancePriceService
from redis_client.redis_client import get_redis
from src.exchanges.use_cases  import CreateExchangeMetricsUseCase
from src.exchanges.use_cases import GetExchangeUseCase
from src.db.db import get_session
from src.exchanges.repository import ExchangeRepository


async def create_use_case(session=Depends(get_session)) -> CreateExchangeMetricsUseCase:
    repo = ExchangeRepository(session)
    binance_service = BinancePriceService()

    return CreateExchangeMetricsUseCase(repo, binance_service)


async def get_use_case(session=Depends(get_session), redis = Depends(get_redis)) -> GetExchangeUseCase:
    repo = ExchangeRepository(session)

    return GetExchangeUseCase(repo, redis)


async def delete_use_case(session=Depends(get_session), redis = Depends(get_redis)) -> DeleteExchangeUseCase:
    repo = ExchangeRepository(session)

    return DeleteExchangeUseCase(repo, redis)