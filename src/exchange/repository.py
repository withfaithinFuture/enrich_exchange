from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from exchange.exchange_entities import Exchange
from exchange.portfolio_interface import IExchangeRepo
from exchange.schemas import ExchangeModel



class ExchangeRepository(IExchangeRepo, ABC):

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, exchange: Exchange) -> Exchange:
        exchange_model = ExchangeModel(
            id=exchange.id,
            exchange_name=exchange.exchange_name,
            trust_score=exchange.trust_score,
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
            trust_score=exchange_model.trust_score,
            btc_price=exchange_model.btc_price,
            eth_price=exchange_model.eth_price,
            sol_price=exchange_model.sol_price
        )