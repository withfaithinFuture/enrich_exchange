from abc import ABC, abstractmethod
from src.shares.user_entities import User


class IUserRepo(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        pass