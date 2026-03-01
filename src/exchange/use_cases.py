import uuid
from random import randint
from src.binance.binance_price_service import BinancePriceService
from src.exchange.exceptions import UnavailableServiceError
from src.exchange.exchange_entities import Exchange
from src.exchange.portfolio_interface import IExchangeRepo
from aiobreaker import CircuitBreakerError
from httpx import RequestError, HTTPError


class CreateExchangeMetricsUseCase:

    def __init__(self, repo: IExchangeRepo, binance_service: BinancePriceService):
        self.repo = repo
        self.binance_service = binance_service


    async def execute(self, exchange_name: str) -> Exchange:

        try:
            prices = await self.binance_service.get_prices()

        except (CircuitBreakerError, HTTPError) as e:
            raise UnavailableServiceError("Binance")


        new_exchange = Exchange(
            id=uuid.uuid4(),
            exchange_name=exchange_name,
            trust_score=randint(0, 10),
            btc_price=prices["BTCUSDT"],
            eth_price=prices["ETHUSDT"],
            sol_price=prices["SOLUSDT"]
        )

        await self.repo.create(new_exchange)
        return new_exchange



class GetExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, create_use_case: CreateExchangeMetricsUseCase):
        self.repo = repo
        self.create_use_case = create_use_case


    async def execute(self, exchange_name: str) -> Exchange:

        exchange = await self.repo.get_by_name(exchange_name)
        if not exchange:
            return await self.create_use_case.execute(exchange_name)

        return exchange