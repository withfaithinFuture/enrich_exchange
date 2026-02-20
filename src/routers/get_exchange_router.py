from uuid import UUID
from fastapi import APIRouter, Depends
from src.app.use_cases.get_exchange import GetExchangeUseCase
from src.routers.dependencies import get_use_case


router = APIRouter(tags=['Actions with exchanges'])


@router.get("/{exchange_name}")
async def get_exchange(exchange_name: str, use_case: GetExchangeUseCase = Depends(get_use_case)):

    exchange = await use_case.execute(exchange_name)

    return exchange