from fastapi import APIRouter, Depends
from src.exchange.use_cases import DeleteExchangeUseCase
from src.exchange.use_cases import UpdateExchangeUseCase
from src.exchange.use_cases import CreateExchangeUseCase
from src.exchange.use_cases import GetExchangeUseCase
from exchange.dependencies import get_use_case, create_use_case, update_use_case, delete_use_case


router = APIRouter(tags=['Actions with exchanges'])


@router.post("/{exchange_name}")
async def create_exchange(exchange_name: str, use_case: CreateExchangeUseCase = Depends(create_use_case)):
    exchange = await use_case.execute(exchange_name)
    return exchange


@router.get("/{exchange_name}")
async def get_exchange(exchange_name: str, use_case: GetExchangeUseCase = Depends(get_use_case)):
    exchange = await use_case.execute(exchange_name)
    return exchange


@router.put("/")
async def update_exchange(exchange_name: str, use_case: UpdateExchangeUseCase = Depends(update_use_case)):
    exchange = await use_case.execute(exchange_name)
    return exchange


@router.delete("/{exchange_id}")
async def delete_exchange(exchange_name: str, use_case: DeleteExchangeUseCase = Depends(delete_use_case)):
    await use_case.execute(exchange_name)
    return {"detail": f"Exchange {exchange_name} deleted"}