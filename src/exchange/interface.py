from abc import ABC, abstractmethod
from src.exchange.exchange_entities import Exchange


class IExchangeRepo(ABC):

    @abstractmethod
    async def create(self, exchange: Exchange) -> Exchange:
        pass


    @abstractmethod
    async def get_by_name(self, exchange_name: str) -> Exchange | None:
        pass