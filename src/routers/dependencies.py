from fastapi import Depends
from src.app.services.binance_price_service import BinancePriceService
from src.app.services.exchange_api_service import ExchangeApiService
from src.app.use_cases.create_exchange import CreateExchangeUseCase
from src.app.use_cases.delete_exchange import DeleteExchangeUseCase
from src.app.use_cases.get_exchange import GetExchangeUseCase
from src.app.use_cases.update_exchange import UpdateExchangeUseCase
from src.domain.interfaces.portfolio_interface import IExchangeRepo
from src.infrastructure.db.db import get_session
from src.infrastructure.db.repository import ExchangeRepository


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