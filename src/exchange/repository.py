from abc import ABC
from dataclasses import asdict, fields
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.exchange.exceptions import NotFoundByNameError
from src.exchange.exchange_entities import Exchange
from src.exchange.interface import IExchangeRepo
from src.exchange.models import ExchangeModel


class ExchangeRepository(IExchangeRepo, ABC):

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, exchange: Exchange) -> Exchange:
        exchange_model = ExchangeModel(**asdict(exchange))

        self.session.add(exchange_model)
        await self.session.flush()

        return exchange


    async def get_by_name(self, exchange_name: str) -> Exchange | None:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange_name)
        result = await self.session.execute(query)
        exchange_model = result.scalar_one_or_none()

        if not exchange_model:
            raise NotFoundByNameError(exchange_name, 'Exchange')

        exchange_args = {}

        for field in fields(Exchange):
            exchange_args[field.name] = getattr(exchange_model, field.name)

        return Exchange(**exchange_args)