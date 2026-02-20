from fastapi import APIRouter, Depends
from src.app.use_cases.create_exchange import CreateExchangeUseCase
from src.app.use_cases.get_exchange import GetExchangeUseCase
from src.domain.entities.exchange import Exchange
from src.infrastructure.db.repository import ExchangeRepository
from src.routers.dependencies import get_use_case, create_use_case

router = APIRouter(tags=['Actions with exchanges'])


@router.post("/{exchange_name}")
async def create_exchange(exchange_name: str, use_case: CreateExchangeUseCase = Depends(create_use_case)):
    exchange = await use_case.execute(exchange_name)
    return exchange