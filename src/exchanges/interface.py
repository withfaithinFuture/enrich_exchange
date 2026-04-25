from abc import ABC, abstractmethod
from src.exchanges.exchange_entities import Exchange


class IExchangeRepo(ABC):

    @abstractmethod
    async def create(self, exchange: Exchange) -> Exchange:
        pass


    @abstractmethod
    async def get_by_name(self, exchange_name: str) -> Exchange | None:
        pass

    @abstractmethod
    async def update(self, exchange: Exchange) -> None:
        pass

    @abstractmethod
    async def delete_by_name(self, exchange_name: str) -> bool:
        pass