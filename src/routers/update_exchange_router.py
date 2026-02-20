from fastapi import APIRouter, Depends
from src.domain.entities.exchange import Exchange
from src.infrastructure.db.repository import ExchangeRepository
from src.app.use_cases.update_exchange import UpdateExchangeUseCase
from src.routers.dependencies import update_use_case


router = APIRouter(prefix="/exchange")

@router.put("/")
async def update_exchange(exchange_name: str, use_case: UpdateExchangeUseCase = Depends(update_use_case)):

    exchange = await use_case.execute(exchange_name)

    return exchange