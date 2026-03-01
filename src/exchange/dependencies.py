from fastapi import Depends
from src.binance.binance_price_service import BinancePriceService
from src.exchange.redis_client import get_redis
from src.exchange.use_cases  import CreateExchangeMetricsUseCase
from src.exchange.use_cases import GetExchangeUseCase
from src.db import get_session
from src.exchange.repository import ExchangeRepository


async def create_use_case(session=Depends(get_session)) -> CreateExchangeMetricsUseCase:
    repo = ExchangeRepository(session)
    binance_service = BinancePriceService()

    return CreateExchangeMetricsUseCase(repo, binance_service)


async def get_use_case(session=Depends(get_session), redis = Depends(get_redis)) -> GetExchangeUseCase:
    repo = ExchangeRepository(session)
    binance_service = BinancePriceService()
    create_case = CreateExchangeMetricsUseCase(repo, binance_service)

    return GetExchangeUseCase(repo, create_case, redis)