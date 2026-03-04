from fastapi import APIRouter, Depends
from starlette import status

from src.exchange.use_cases import CreateExchangeMetricsUseCase
from src.exchange.use_cases import GetExchangeUseCase
from src.exchange.dependencies import get_use_case, create_use_case


router = APIRouter(tags=['Actions with exchanges'])


@router.post("/exchange/{exchange_name}", status_code=status.HTTP_201_CREATED)
async def create_exchange(exchange_name: str, create_case: CreateExchangeMetricsUseCase = Depends(create_use_case)):
    return await create_case.create_exchange_metrics(exchange_name)


@router.get("/exchange/{exchange_name}", status_code=status.HTTP_200_OK)
async def get_exchange(exchange_name: str, get_case: GetExchangeUseCase = Depends(get_use_case)):
    return await get_case.get_exchange_by_name(exchange_name)