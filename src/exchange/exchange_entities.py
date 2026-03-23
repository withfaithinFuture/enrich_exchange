from dataclasses import dataclass
from uuid import UUID
from pydantic import BaseModel, ConfigDict


@dataclass
class Exchange:
    id: UUID
    exchange_name: str
    trust_score: int


    btc_price: float
    eth_price: float
    sol_price: float