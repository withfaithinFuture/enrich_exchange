from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from src.domain.entities.exchange import Exchange
from src.domain.interfaces.portfolio_interface import IExchangeRepo
from src.infrastructure.db.models import ExchangeModel



class ExchangeRepository(IExchangeRepo, ABC):

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, exchange: Exchange) -> Exchange:
        exchange_model = ExchangeModel(
            id=exchange.id,
            exchange_name=exchange.exchange_name,
            work_in_russia=exchange.work_in_russia,
            volume=exchange.volume,
            owner_first_name=exchange.owner_first_name,
            owner_last_name=exchange.owner_last_name,
            btc_price=exchange.btc_price,
            eth_price=exchange.eth_price,
            sol_price=exchange.sol_price
        )

        self.session.add(exchange_model)
        await self.session.flush()

        return exchange


    async def get_by_name(self, exchange_name: str) -> Exchange | None:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange_name)
        result = await self.session.execute(query)
        exchange_model = result.scalar_one_or_none()

        if not exchange_model:
            return None

        return Exchange(
            id=exchange_model.id,
            exchange_name=exchange_model.exchange_name,
            work_in_russia=exchange_model.work_in_russia,
            volume=exchange_model.volume,
            owner_first_name=exchange_model.owner_first_name,
            owner_last_name=exchange_model.owner_last_name,
            btc_price=exchange_model.btc_price,
            eth_price=exchange_model.eth_price,
            sol_price=exchange_model.sol_price
        )


    async def update(self, exchange: Exchange) -> Exchange | None:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange.exchange_name)
        result = await self.session.execute(query)
        exchange_model = result.scalar_one_or_none()

        exchange_model.exchange_name = exchange.exchange_name
        exchange_model.work_in_russia = exchange.work_in_russia
        exchange_model.volume = exchange.volume
        exchange_model.owner_first_name = exchange.owner_first_name
        exchange_model.owner_last_name = exchange.owner_last_name
        exchange_model.btc_price = exchange.btc_price
        exchange_model.eth_price = exchange.eth_price
        exchange_model.sol_price = exchange.sol_price

        await self.session.flush()
        await self.session.refresh(exchange_model)

        return exchange


    async def delete_by_name(self, exchange_name: str) -> None:
        query = select(ExchangeModel).where(ExchangeModel.exchange_name == exchange_name)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        await self.session.delete(model)