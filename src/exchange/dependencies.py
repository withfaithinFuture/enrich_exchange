from fastapi import Depends
from binance.binance_price_service import BinancePriceService
from src.exchange.use_cases  import CreateExchangeMetricsUseCase
from src.exchange.use_cases import GetExchangeUseCase
from db import get_session
from exchange.repository import ExchangeRepository


def get_binance_service() -> BinancePriceService:
    return BinancePriceService()


async def get_exchange_repo(session=Depends(get_session)) -> ExchangeRepository:
    return ExchangeRepository(session)


async def create_use_case(repo: ExchangeRepository = Depends(get_exchange_repo), binance_service: BinancePriceService = Depends(get_binance_service)) -> CreateExchangeMetricsUseCase:
    return CreateExchangeMetricsUseCase(repo, binance_service)


async def get_use_case(repo: ExchangeRepository = Depends(get_exchange_repo), create_case: CreateExchangeMetricsUseCase = Depends(create_use_case)) -> GetExchangeUseCase:
    return GetExchangeUseCase(repo, create_case)