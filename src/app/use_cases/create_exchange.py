import uuid
from uuid import uuid4

from src.app.services.binance_price_service import BinancePriceService
from src.domain.entities.exchange import Exchange
from src.domain.interfaces.portfolio_interface import IExchangeRepo
from src.app.services.exchange_api_service import ExchangeApiService


class CreateExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, exchange_api_service: ExchangeApiService, binance_service: BinancePriceService):
        self.repo = repo
        self.exchange_api = exchange_api_service
        self.binance_service = binance_service


    async def execute(self, exchange_name: str) -> Exchange | None:
        external_exchanges = await self.exchange_api.get_exchanges()
        external_exchange = None
        for exchange in external_exchanges:
            if exchange["exchange_name"] == exchange_name:
                external_exchange = exchange
                break

        if not external_exchange:
            return None

        prices = await self.binance_service.get_prices()

        local_exchange = Exchange(
            id=uuid.uuid4(),
            exchange_name=external_exchange["exchange_name"],
            work_in_russia=external_exchange["work_in_Russia"],
            volume=external_exchange["volume"],
            owner_first_name=external_exchange["owner"]["first_name"],
            owner_last_name=external_exchange["owner"]["last_name"],
            btc_price=prices.get("BTCUSDT"),
            eth_price=prices.get("ETHUSDT"),
            sol_price=prices.get("SOLUSDT")
        )

        await self.repo.create(local_exchange)

        return local_exchange
