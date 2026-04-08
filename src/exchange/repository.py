from abc import ABC
from dataclasses import asdict, fields
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.exchange.exchange_entities import Exchange
from src.exchange.interface import IExchangeRepo
from src.exchange.models import ExchangeModel


class ExchangeRepository(IExchangeRepo, ABC):

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, exchange: Exchange) -> Exchange:
        exchange_model = ExchangeModel(**asdict(exchange))
        self.session.add(exchange_model)
        return exchange


    async def get_by_name(self, exchange_name: str) -> Exchange | None:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange_name)
        result = await self.session.execute(query)
        exchange_model = result.scalar_one_or_none()

        if exchange_model:
            exchange_args = {}

            for field in fields(Exchange):
                exchange_args[field.name] = getattr(exchange_model, field.name)

            return Exchange(**exchange_args)

        return exchange_model


    async def update(self, exchange: Exchange) -> Exchange:
        await self.session.flush()
        await self.session.refresh(exchange)
        return exchange


    async def delete_by_name(self, exchange_name: str) -> bool:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange_name)
        result = await self.session.execute(query)
        exchange_data = result.scalar_one_or_none()

        if exchange_data:
            await self.session.delete(exchange_data)
            return True

        return False