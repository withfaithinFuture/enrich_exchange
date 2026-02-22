from dataclasses import dataclass
from uuid import UUID


@dataclass
class Exchange:
    id: UUID
    exchange_name: str
    work_in_russia: bool
    volume: int
    owner_first_name: str
    owner_last_name: str

    btc_price: None | float = None
    eth_price: None | float = None
    sol_price: None | float = None