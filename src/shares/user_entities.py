from uuid import UUID
from dataclasses import dataclass


@dataclass
class User:
    user_id: UUID
    username: str
    email: str
    shares_broker: str
    broker_commission: float