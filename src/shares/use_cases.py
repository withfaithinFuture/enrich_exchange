import uuid
from src.shares.interface import IUserRepo
from src.shares.user_entities import User


class CreateUserInfoUseCase:

    def __init__(self, repo: IUserRepo):
        self.repo = repo


    def set_commission(self, shares_broker: str):
        commissions = {
            't-bank': 0.015,
            'vtb': 0.03,
            'Sber': 0.025,
            'Alfa-Bank': 0.035,
            'Gazprombank': 0.04
        }

        if shares_broker in commissions:
            return commissions[shares_broker]
        else:
            return 0.1


    async def create_user_commission(self, username: str, email: str, shares_broker: str):
        user_commission = self.set_commission(shares_broker)
        new_user = User(
            user_id=uuid.uuid4(),
            username=username,
            email=email,
            shares_broker=shares_broker,
            broker_commission=user_commission
        )

        await self.repo.create(user=new_user)
        return new_user



