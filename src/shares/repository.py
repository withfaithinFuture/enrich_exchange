from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from src.shares.interface import IUserRepo
from src.shares.user_entities import User
from src.shares.models import UserSharesModel


class UserSharesRepository(IUserRepo):

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, user: User) -> User:
        user_model = UserSharesModel(**asdict(user))
        self.session.add(user_model)
        return user