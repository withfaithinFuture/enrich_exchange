from fastapi import Depends
from binance.binance_price_service import BinancePriceService
from first_service.exchange_api_service import ExchangeApiService
from src.exchange.use_cases  import CreateExchangeUseCase
from src.exchange.use_cases  import DeleteExchangeUseCase
from src.exchange.use_cases import GetExchangeUseCase
from src.exchange.use_cases import UpdateExchangeUseCase
from exchange.portfolio_interface import IExchangeRepo
from db import get_session
from exchange.repository import ExchangeRepository


async def get_use_case(session=Depends(get_session)):
    repo = ExchangeRepository(session)
    exchange_api_service = ExchangeApiService()
    binance_service = BinancePriceService()
    return GetExchangeUseCase(repo, exchange_api_service, binance_service)


async def create_use_case(session=Depends(get_session)):
    repo = ExchangeRepository(session)
    exchange_api_service = ExchangeApiService()
    binance_service = BinancePriceService()
    return CreateExchangeUseCase(repo, exchange_api_service, binance_service)


async def update_use_case(session=Depends(get_session)):
    repo = IExchangeRepo(session)
    exchange_api_service = ExchangeApiService()
    binance_service = BinancePriceService()
    get_use_case_update = GetExchangeUseCase(repo, exchange_api_service, binance_service)
    return UpdateExchangeUseCase(get_use_case_update)



async def delete_use_case(session=Depends(get_session)):
    repo = ExchangeRepository(session)
    return DeleteExchangeUseCase(repo)