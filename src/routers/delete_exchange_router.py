from uuid import UUID
from fastapi import APIRouter, Depends
from src.app.use_cases.delete_exchange import DeleteExchangeUseCase
from src.infrastructure.db.db import get_session
from src.infrastructure.db.repository import ExchangeRepository
from src.routers.dependencies import delete_use_case


router = APIRouter(prefix="/exchange")

@router.delete("/{exchange_id}")
async def delete_exchange(exchange_name: str, use_case: DeleteExchangeUseCase = Depends(delete_use_case)):
    await use_case.execute(exchange_name)

    return {"detail": f"Exchange {exchange_name} deleted"}